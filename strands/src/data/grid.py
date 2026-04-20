import random
import time
import os

ROWS = 6
COLS = 8

DIRS_8 = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1),
]

DIRS_4 = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
]


class SearchTimeout(Exception):
    pass


class SearchController:
    def __init__(self, max_seconds=120, progress_every_seconds=5.0):
        self.started_at = time.monotonic()
        self.deadline = self.started_at + max_seconds
        self.progress_every_seconds = progress_every_seconds
        self.last_progress_at = self.started_at
        self.max_seconds = max_seconds
        self.stats = {
            "spangram_attempts": 0,
            "region_assignments": 0,
            "region_path_dfs_nodes": 0,
            "region_backtrack_states": 0,
            "uniqueness_dfs_nodes": 0,
        }

    def check(self):
        self.report()
        if time.monotonic() > self.deadline:
            raise SearchTimeout()

    def bump(self, key, n=1):
        self.stats[key] = self.stats.get(key, 0) + n
        now = time.monotonic()
        if now - self.last_progress_at >= self.progress_every_seconds:
            self.report()

    def elapsed(self):
        return time.monotonic() - self.started_at

    def report(self, force=False, context="progress"):
        now = time.monotonic()
        if not force and (now - self.last_progress_at) < self.progress_every_seconds:
            return
        self.last_progress_at = now
        print(
            "[search] "
            f"{context} elapsed={self.elapsed():.1f}s "
            f"spangram_attempts={self.stats['spangram_attempts']} "
            f"region_assignments={self.stats['region_assignments']} "
            f"region_path_dfs_nodes={self.stats['region_path_dfs_nodes']} "
            f"region_backtrack_states={self.stats['region_backtrack_states']} "
            f"uniqueness_dfs_nodes={self.stats['uniqueness_dfs_nodes']}"
        )


def create_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def copy_grid(grid):
    return [row[:] for row in grid]


def print_grid(grid):
    for row in grid:
        print(" ".join(cell if cell is not None else "." for cell in row))
    print()


def get_neighbors(r, c, dirs):
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc


def place_word(grid, path, word):
    for (r, c), ch in zip(path, word):
        grid[r][c] = ch


def clear_path(grid, path):
    for r, c in path:
        grid[r][c] = None


def canonical_segment(a, b):
    return tuple(sorted((a, b)))


def path_segments(path):
    return [canonical_segment(path[i], path[i + 1]) for i in range(len(path) - 1)]


def segments_cross(seg1, seg2):
    (a1, a2) = seg1
    (b1, b2) = seg2

    # Ignore touching segments; cell overlap is checked separately.
    if a1 == b1 or a1 == b2 or a2 == b1 or a2 == b2:
        return False

    ax1, ay1 = a1
    ax2, ay2 = a2
    bx1, by1 = b1
    bx2, by2 = b2

    # In this grid, true visual crossing without shared endpoints happens
    # only for opposite diagonals across the same 2x2 square.
    da_x = ax2 - ax1
    da_y = ay2 - ay1
    db_x = bx2 - bx1
    db_y = by2 - by1

    return (
        abs(da_x) == 1
        and abs(da_y) == 1
        and abs(db_x) == 1
        and abs(db_y) == 1
        and (ax1 + ax2) == (bx1 + bx2)
        and (ay1 + ay2) == (by1 + by2)
        and (da_x * db_x + da_y * db_y) == 0
    )


def paths_conflict(path_a, path_b):
    if set(path_a) & set(path_b):
        return True

    seg_a = path_segments(path_a)
    seg_b = path_segments(path_b)
    for sa in seg_a:
        for sb in seg_b:
            if segments_cross(sa, sb):
                return True
    return False


def path_compatible_with_existing(path, existing_paths):
    for existing in existing_paths:
        if paths_conflict(path, existing):
            return False
    return True


def path_has_self_crossing(path):
    if len(path) < 4:
        return False

    segments = path_segments(path)
    for i in range(len(segments)):
        for j in range(i + 2, len(segments)):
            if segments_cross(segments[i], segments[j]):
                return True
    return False


def can_extend_path_without_self_cross(path, next_cell):
    if len(path) < 2:
        return True

    a = path[-1]
    b = next_cell
    dr = b[0] - a[0]
    dc = b[1] - a[1]

    # Only diagonal segments can visually cross in this grid model.
    if abs(dr) != 1 or abs(dc) != 1:
        return True

    opposite = canonical_segment((a[0], b[1]), (b[0], a[1]))
    for i in range(len(path) - 1):
        if canonical_segment(path[i], path[i + 1]) == opposite:
            return False
    return True


def all_paths_compatible(paths):
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if paths_conflict(paths[i], paths[j]):
                return False
    return True


def _is_edge_cell(cell):
    r, c = cell
    return r == 0 or r == ROWS - 1 or c == 0 or c == COLS - 1


def _edge_id(cell):
    r, c = cell
    edges = set()
    if r == 0:
        edges.add("top")
    if r == ROWS - 1:
        edges.add("bottom")
    if c == 0:
        edges.add("left")
    if c == COLS - 1:
        edges.add("right")
    return edges


def _path_spans_opposite_edges(path):
    touched_edges = set()
    for cell in path:
        touched_edges.update(_edge_id(cell))
    return (
        ("left" in touched_edges and "right" in touched_edges)
        or ("top" in touched_edges and "bottom" in touched_edges)
    )


def _path_turn_count(path):
    turns = 0
    for i in range(2, len(path)):
        dr1 = path[i - 1][0] - path[i - 2][0]
        dc1 = path[i - 1][1] - path[i - 2][1]
        dr2 = path[i][0] - path[i - 1][0]
        dc2 = path[i][1] - path[i - 1][1]
        if (dr1, dc1) != (dr2, dc2):
            turns += 1
    return turns


def _path_bbox_area(path):
    rows = [r for r, _ in path]
    cols = [c for _, c in path]
    return (max(rows) - min(rows) + 1) * (max(cols) - min(cols) + 1)


def _path_has_reversal(path):
    for i in range(2, len(path)):
        dr1 = path[i - 1][0] - path[i - 2][0]
        dc1 = path[i - 1][1] - path[i - 2][1]
        dr2 = path[i][0] - path[i - 1][0]
        dc2 = path[i][1] - path[i - 1][1]
        if (dr2, dc2) == (-dr1, -dc1):
            return True
    return False


def _count_small_open_regions(used_cells, min_region_size=4):
    all_cells = {(r, c) for r in range(ROWS) for c in range(COLS)}
    open_cells = all_cells - set(used_cells)
    seen = set()
    small_regions = 0

    for cell in open_cells:
        if cell in seen:
            continue
        stack = [cell]
        size = 0
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            size += 1
            r, c = cur
            for nr, nc in get_neighbors(r, c, DIRS_4):
                if (nr, nc) in open_cells and (nr, nc) not in seen:
                    stack.append((nr, nc))
        if size < min_region_size:
            small_regions += 1

    return small_regions


def _ribbon_contact_score(path, candidate):
    # Prefer "out-and-back" structure where later segments run close and parallel
    # to earlier segments, but avoid immediate local clustering.
    if len(path) < 4:
        return 0.0

    r, c = candidate
    score = 0.0
    # Skip the most recent cells to avoid rewarding tiny zigzags.
    for pr, pc in path[:-3]:
        manhattan = abs(pr - r) + abs(pc - c)
        if manhattan == 1:
            score += 0.35
        elif manhattan == 2:
            score += 0.12
    return score


def _long_path_quality_ok(path):
    if not path or not _is_edge_cell(path[0]) or not _is_edge_cell(path[-1]):
        return False

    # A spangram must connect opposite sides (left-right or top-bottom).
    if not _path_spans_opposite_edges(path):
        return False

    # Avoid tiny edge-hugging paths for longer spangrams.
    if len(path) >= 11:
        turns = _path_turn_count(path)
        bbox_area = _path_bbox_area(path)
        touched_edges = set()
        for cell in path:
            touched_edges.update(_edge_id(cell))
        if turns < 4:
            return False
        if bbox_area < min(18, ROWS * COLS):
            return False
        if len(touched_edges) < 2:
            return False
        if not _path_has_reversal(path) and len(touched_edges) < 3:
            return False
        if _count_small_open_regions(path, min_region_size=4) > 0:
            return False

    return True


def _generate_spangram_path_long(spangram, max_attempts=1200, controller=None):
    target_len = len(spangram)
    edge_cells = [
        (r, c)
        for r in range(ROWS)
        for c in range(COLS)
        if _is_edge_cell((r, c))
    ]

    for _ in range(max_attempts):
        if controller is not None:
            controller.check()

        start = random.choice(edge_cells)
        visited = {start}
        path = [start]

        # Bounded DFS per attempt so long mode stays responsive.
        nodes = 0
        max_nodes = 10000
        result = None

        def dfs(last_dir=None):
            nonlocal nodes, result
            if result is not None:
                return
            if controller is not None:
                controller.check()

            nodes += 1
            if nodes > max_nodes:
                return

            if len(path) == target_len:
                if _long_path_quality_ok(path):
                    result = path[:]
                return

            r, c = path[-1]
            candidates = []
            for nr, nc in get_neighbors(r, c, DIRS_8):
                if (nr, nc) in visited:
                    continue
                if not can_extend_path_without_self_cross(path, (nr, nc)):
                    continue

                dr = nr - r
                dc = nc - c
                score = 0.0

                # Favor turns/curves over long straight segments.
                if last_dir is not None:
                    if (dr, dc) != last_dir:
                        score += 1.8
                    else:
                        score -= 0.6
                    if (dr, dc) == (-last_dir[0], -last_dir[1]):
                        score += 1.0

                # Encourage broad coverage to reduce simple straight sweeps.
                rows = [p[0] for p in path]
                cols = [p[1] for p in path]
                cur_area = (max(rows) - min(rows) + 1) * (max(cols) - min(cols) + 1)
                new_rows = rows + [nr]
                new_cols = cols + [nc]
                new_area = (max(new_rows) - min(new_rows) + 1) * (max(new_cols) - min(new_cols) + 1)
                if new_area > cur_area:
                    score += 0.8

                # Slightly prefer staying in 4-neighbor motion most of the time.
                if abs(dr) + abs(dc) == 1:
                    score += 0.2

                # Favor compact "ribbon" shapes over chaotic global snaking.
                score += _ribbon_contact_score(path, (nr, nc))

                # Avoid creating tiny disconnected pockets while drawing path.
                trial_used = visited | {(nr, nc)}
                tiny_regions = _count_small_open_regions(trial_used, min_region_size=4)
                score -= 2.4 * tiny_regions

                # Keep randomness so we get diverse shapes.
                score += random.random() * 0.5
                candidates.append((score, (nr, nc), (dr, dc)))

            if not candidates:
                return

            candidates.sort(key=lambda x: x[0], reverse=True)
            # Limit branching; this keeps speed stable while still exploring alternatives.
            for _, (nr, nc), new_dir in candidates[:6]:
                visited.add((nr, nc))
                path.append((nr, nc))
                dfs(last_dir=new_dir)
                if result is not None:
                    return
                path.pop()
                visited.remove((nr, nc))

        dfs()
        if result is not None and not path_has_self_crossing(result):
            return result

    return None


def _generate_spangram_path_classic(spangram, max_attempts=500, controller=None):
    for _ in range(max_attempts):
        if controller is not None:
            controller.check()
        orientation = random.choice(["horizontal", "vertical"])

        if orientation == "horizontal":
            start_row = random.randint(0, ROWS - 1)
            start = (start_row, 0)
        else:
            start_col = random.randint(0, COLS - 1)
            start = (0, start_col)

        path = [start]
        visited = {start}

        while len(path) < len(spangram):
            if controller is not None:
                controller.check()
            r, c = path[-1]
            candidates = []

            if orientation == "horizontal":
                if c + 1 < COLS and (r, c + 1) not in visited:
                    candidates.append((r, c + 1))
                for dr in (-1, 1):
                    nr = r + dr
                    if (
                        0 <= nr < ROWS
                        and abs(nr - start_row) <= 2
                        and c + 1 < COLS
                        and (nr, c + 1) not in visited
                    ):
                        candidates.append((nr, c + 1))
                if not candidates:
                    for dr in (-1, 0, 1):
                        nr = r + dr
                        if (
                            0 <= nr < ROWS
                            and abs(nr - start_row) <= 2
                            and (nr, c) not in visited
                        ):
                            candidates.append((nr, c))
            else:
                if r + 1 < ROWS and (r + 1, c) not in visited:
                    candidates.append((r + 1, c))
                for dc in (-1, 1):
                    nc = c + dc
                    if (
                        0 <= nc < COLS
                        and abs(nc - start_col) <= 2
                        and r + 1 < ROWS
                        and (r + 1, nc) not in visited
                    ):
                        candidates.append((r + 1, nc))
                if not candidates:
                    for dc in (-1, 0, 1):
                        nc = c + dc
                        if (
                            0 <= nc < COLS
                            and abs(nc - start_col) <= 2
                            and (r, nc) not in visited
                        ):
                            candidates.append((r, nc))

            if not candidates:
                break

            next_pos = random.choice(candidates)
            path.append(next_pos)
            visited.add(next_pos)

        if len(path) != len(spangram):
            continue

        if orientation == "horizontal" and not any(c == COLS - 1 for _, c in path):
            continue
        if orientation == "vertical" and not any(r == ROWS - 1 for r, _ in path):
            continue

        # Defensive validation: classic mode should always be a true side-to-side span.
        if not _path_spans_opposite_edges(path):
            continue

        if path_has_self_crossing(path):
            continue

        return path

    return None


def generate_spangram_path(
    spangram,
    max_attempts=500,
    mode="auto",
    long_threshold=11,
    controller=None,
):
    mode = (mode or "auto").strip().lower()
    use_long = mode == "long" or (mode == "auto" and len(spangram) >= long_threshold)

    if use_long:
        path = _generate_spangram_path_long(
            spangram,
            max_attempts=max_attempts,
            controller=controller,
        )
        if path is not None:
            return path
        if mode == "long":
            return None

    return _generate_spangram_path_classic(
        spangram,
        max_attempts=max_attempts,
        controller=controller,
    )


def get_regions(grid):
    visited = set()
    regions = []

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is not None or (r, c) in visited:
                continue

            stack = [(r, c)]
            region = []
            while stack:
                cr, cc = stack.pop()
                if (cr, cc) in visited:
                    continue
                visited.add((cr, cc))
                region.append((cr, cc))
                for nr, nc in get_neighbors(cr, cc, DIRS_4):
                    if grid[nr][nc] is None and (nr, nc) not in visited:
                        stack.append((nr, nc))
            regions.append(region)

    return regions


def assign_words_to_regions(regions, words, controller=None):
    region_sizes = [len(r) for r in regions]
    words_sorted = sorted(words, key=len, reverse=True)
    results = []

    def subset(words_left, target, start=0, path=None):
        if controller is not None:
            controller.check()
        if path is None:
            path = []
        if target == 0:
            yield path[:]
            return
        for j in range(start, len(words_left)):
            w = words_left[j]
            if len(w) <= target:
                yield from subset(words_left, target - len(w), j + 1, path + [w])

    def backtrack(i, remaining_words, current_assignment):
        if controller is not None:
            controller.check()
        if i == len(regions):
            if not remaining_words:
                results.append([group[:] for group in current_assignment])
            return

        size = region_sizes[i]
        for group in subset(remaining_words, size):
            new_remaining = remaining_words[:]
            for w in group:
                new_remaining.remove(w)
            backtrack(i + 1, new_remaining, current_assignment + [group])

    backtrack(0, words_sorted, [])
    return results


def enumerate_region_paths_by_length(region_cells, lengths, controller=None):
    region_set = set(region_cells)
    all_paths = {length: [] for length in lengths}

    def dfs(path, visited, target_len):
        if controller is not None:
            controller.check()
            controller.bump("region_path_dfs_nodes")
        if len(path) == target_len:
            all_paths[target_len].append(path[:])
            return

        r, c = path[-1]
        for nr, nc in get_neighbors(r, c, DIRS_8):
            if (nr, nc) in region_set and (nr, nc) not in visited:
                visited.add((nr, nc))
                path.append((nr, nc))
                dfs(path, visited, target_len)
                path.pop()
                visited.remove((nr, nc))

    for length in lengths:
        for start in region_cells:
            dfs([start], {start}, length)

    return all_paths


def solve_region_paths(region_cells, words, controller=None):
    if not words:
        return []

    lengths = sorted({len(w) for w in words})
    raw_paths_by_len = enumerate_region_paths_by_length(region_cells, lengths, controller=controller)
    paths_by_len = {
        length: [(path, frozenset(path)) for path in raw_paths_by_len[length]]
        for length in lengths
    }

    for word in words:
        if not paths_by_len[len(word)]:
            return None

    word_indices = tuple(range(len(words)))
    assigned = {}
    used_cells = set()
    memo_dead_states = set()

    def backtrack(remaining):
        if controller is not None:
            controller.check()
            controller.bump("region_backtrack_states")
        if not remaining:
            return True

        state_key = (remaining, frozenset(used_cells))
        if state_key in memo_dead_states:
            return False

        best_idx = None
        best_paths = None

        for idx in remaining:
            candidates = []
            for path, path_set in paths_by_len[len(words[idx])]:
                if path_set.isdisjoint(used_cells) and path_compatible_with_existing(path, assigned.values()):
                    candidates.append((path, path_set))
            if not candidates:
                memo_dead_states.add(state_key)
                return False
            if best_paths is None or len(candidates) < len(best_paths):
                best_idx = idx
                best_paths = candidates

        random.shuffle(best_paths)
        next_remaining = tuple(idx for idx in remaining if idx != best_idx)

        for path, path_set in best_paths:
            assigned[best_idx] = path
            used_cells.update(path_set)

            if backtrack(next_remaining):
                return True

            del assigned[best_idx]
            used_cells.difference_update(path_set)

        memo_dead_states.add(state_key)
        return False

    if not backtrack(word_indices):
        return None

    return [assigned[i] for i in range(len(words))]


def solve_region_paths_fast(
    region_cells,
    words,
    max_trials=12,
    per_step_candidates=40,
    controller=None,
):
    if not words:
        return []

    # Place longer words first; they are usually the most constrained.
    order = sorted(range(len(words)), key=lambda i: len(words[i]), reverse=True)

    for _ in range(max_trials):
        assigned = {}
        used_cells = set()

        def backtrack(pos):
            if pos == len(order):
                return True

            idx = order[pos]
            length = len(words[idx])

            candidates = sample_paths_in_region(
                region_cells,
                length,
                blocked_cells=used_cells,
                max_paths=per_step_candidates * 2,
                controller=controller,
            )
            if not candidates:
                return False

            random.shuffle(candidates)
            existing_paths = list(assigned.values())

            tried = 0
            for path in candidates:
                if tried >= per_step_candidates:
                    break
                path_set = set(path)
                if not path_set.isdisjoint(used_cells):
                    continue
                if not path_compatible_with_existing(path, existing_paths):
                    continue

                tried += 1
                assigned[idx] = path
                used_cells.update(path_set)

                if backtrack(pos + 1):
                    return True

                del assigned[idx]
                used_cells.difference_update(path_set)

            return False

        if backtrack(0):
            return [assigned[i] for i in range(len(words))]

    return None


def has_exactly_one_path(grid, word, intended_path, controller=None):
    count = 0
    intended_found = False

    def dfs(r, c, i, path, visited):
        nonlocal count, intended_found

        if controller is not None:
            controller.check()
            controller.bump("uniqueness_dfs_nodes")

        if count > 1:
            return

        if i == len(word):
            count += 1
            if path == intended_path:
                intended_found = True
            return

        for nr, nc in get_neighbors(r, c, DIRS_8):
            if (nr, nc) in visited:
                continue
            if grid[nr][nc] != word[i]:
                continue
            visited.add((nr, nc))
            path.append((nr, nc))
            dfs(nr, nc, i + 1, path, visited)
            path.pop()
            visited.remove((nr, nc))

    first_char = word[0]
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] != first_char:
                continue
            dfs(r, c, 1, [(r, c)], {(r, c)})
            if count > 1:
                return False

    return count == 1 and intended_found


def count_word_paths_limited(grid, word, intended_path=None, limit=2):
    count = 0
    intended_found = False

    def dfs(r, c, i, path, visited):
        nonlocal count, intended_found
        if count >= limit:
            return
        if i == len(word):
            count += 1
            if intended_path is not None and path == intended_path:
                intended_found = True
            return

        for nr, nc in get_neighbors(r, c, DIRS_8):
            if (nr, nc) in visited:
                continue
            if grid[nr][nc] != word[i]:
                continue
            visited.add((nr, nc))
            path.append((nr, nc))
            dfs(nr, nc, i + 1, path, visited)
            path.pop()
            visited.remove((nr, nc))

    first_char = word[0]
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] != first_char:
                continue
            dfs(r, c, 1, [(r, c)], {(r, c)})
            if count >= limit:
                return count, intended_found

    return count, intended_found


def is_globally_unique(grid, placed_words, controller=None):
    seen_words = set()
    for word, _ in placed_words:
        if word in seen_words:
            return False
        seen_words.add(word)

    all_paths = [path for _, path in placed_words]
    if not all_paths_compatible(all_paths):
        return False

    for word, path in placed_words:
        if not has_exactly_one_path(grid, word, path, controller=controller):
            return False

    return True


def sample_paths_in_region(region_cells, length, blocked_cells, max_paths=250, controller=None):
    region_set = set(region_cells)
    blocked = set(blocked_cells)
    paths = []

    starts = [cell for cell in region_cells if cell not in blocked]
    random.shuffle(starts)

    def dfs(path, visited):
        if controller is not None:
            controller.check()
        if len(paths) >= max_paths:
            return
        if len(path) == length:
            paths.append(path[:])
            return

        r, c = path[-1]
        neighbors = list(get_neighbors(r, c, DIRS_8))
        random.shuffle(neighbors)
        for nr, nc in neighbors:
            if len(paths) >= max_paths:
                return
            if (nr, nc) in blocked or (nr, nc) in visited or (nr, nc) not in region_set:
                continue
            visited.add((nr, nc))
            path.append((nr, nc))
            dfs(path, visited)
            path.pop()
            visited.remove((nr, nc))

    for start in starts:
        if len(paths) >= max_paths:
            break
        dfs([start], {start})

    # Validate: reject any paths with self-crossing before returning.
    return [p for p in paths if not path_has_self_crossing(p)]


def get_ambiguity_count(grid, placed_words):
    bad = 0
    for entry in placed_words:
        count, intended_found = count_word_paths_limited(
            grid,
            entry["word"],
            intended_path=entry["path"],
            limit=2,
        )
        if count != 1 or not intended_found:
            bad += 1
    return bad


def repair_ambiguities(grid, placed_words, regions, max_iterations=200, controller=None):
    for _ in range(max_iterations):
        if controller is not None:
            controller.check()
        score = get_ambiguity_count(grid, placed_words)
        if score == 0:
            return True

        random.shuffle(placed_words)
        improved = False

        for idx, entry in enumerate(placed_words):
            # Keep spangram fixed in fast mode to avoid expensive global reshaping.
            if entry.get("type") == "spangram":
                continue

            count, intended_found = count_word_paths_limited(
                grid,
                entry["word"],
                intended_path=entry["path"],
                limit=2,
            )
            if count == 1 and intended_found:
                continue

            occupied = set()
            other_paths = []
            for j, other in enumerate(placed_words):
                if j == idx:
                    continue
                occupied.update(other["path"])
                other_paths.append(other["path"])

            clear_path(grid, entry["path"])
            candidates = sample_paths_in_region(
                regions[entry["region_idx"]],
                len(entry["word"]),
                blocked_cells=occupied,
                max_paths=60,
                controller=controller,
            )
            random.shuffle(candidates)

            best_path = None
            best_score = score

            for path in candidates[:20]:
                if not path_compatible_with_existing(path, other_paths):
                    continue
                place_word(grid, path, entry["word"])
                old_path = entry["path"]
                entry["path"] = path
                new_score = get_ambiguity_count(grid, placed_words)
                entry["path"] = old_path
                clear_path(grid, path)

                if new_score < best_score:
                    best_score = new_score
                    best_path = path
                    if new_score == 0:
                        break

            if best_path is not None:
                entry["path"] = best_path
                place_word(grid, best_path, entry["word"])
                improved = True
                break

            place_word(grid, entry["path"], entry["word"])

        if not improved:
            return False

    return get_ambiguity_count(grid, placed_words) == 0


def can_assign_words_to_regions(grid, theme_words):
    regions = get_regions(grid)
    if len(regions) > len(theme_words):
        return False

    # Fast pre-check: each region must be large enough to hold at least
    # the shortest theme word, otherwise assignment is impossible.
    min_word_len = min(len(w) for w in theme_words)
    if any(len(region) < min_word_len for region in regions):
        return False

    return len(assign_words_to_regions(regions, theme_words)) > 0


def place_spangram(
    grid,
    spangram,
    theme_words=None,
    max_attempts=1000,
    controller=None,
    spangram_mode="auto",
    long_threshold=11,
):
    for _ in range(max_attempts):
        if controller is not None:
            controller.check()
        path = generate_spangram_path(
            spangram,
            mode=spangram_mode,
            long_threshold=long_threshold,
            controller=controller,
        )
        if path is None:
            continue

        place_word(grid, path, spangram)
        if theme_words is None or can_assign_words_to_regions(grid, theme_words):
            return path
        clear_path(grid, path)

    return None


def solve_theme_words_globally(base_grid, spangram, spangram_path, theme_words, controller=None):
    regions = sorted(get_regions(base_grid), key=len, reverse=True)
    assignments = assign_words_to_regions(regions, theme_words, controller=controller)
    random.shuffle(assignments)

    if not assignments:
        return None, None

    for assignment in assignments:
        if controller is not None:
            controller.check()
            controller.bump("region_assignments")
        grid = copy_grid(base_grid)
        placed_words = [(spangram, spangram_path)]
        placement_ok = True

        for region, words_in_region in zip(regions, assignment):
            region_paths = solve_region_paths(region, words_in_region, controller=controller)
            if region_paths is None:
                placement_ok = False
                break

            for word, path in zip(words_in_region, region_paths):
                place_word(grid, path, word)
                placed_words.append((word, path))

        if placement_ok and is_globally_unique(grid, placed_words, controller=controller):
            return grid, assignment

    return None, None


def solve_theme_words_fast(base_grid, spangram, spangram_path, theme_words, controller=None):
    regions = sorted(get_regions(base_grid), key=len, reverse=True)
    assignments = assign_words_to_regions(regions, theme_words, controller=controller)
    random.shuffle(assignments)

    if not assignments:
        return None, None

    # Only sample a smaller subset of assignments for speed.
    assignments = assignments[: min(len(assignments), 6)]

    for assignment in assignments:
        if controller is not None:
            controller.check()
            controller.bump("region_assignments")
            controller.report()

        grid = copy_grid(base_grid)
        placed_words = [{
            "word": spangram,
            "path": spangram_path,
            "type": "spangram",
            "region_idx": -1,
        }]

        placement_ok = True
        for region_idx, (region, words_in_region) in enumerate(zip(regions, assignment)):
            # Use bounded stochastic search in fast mode so a single region does
            # not monopolize the entire run.
            region_paths = solve_region_paths_fast(
                region,
                words_in_region,
                max_trials=10,
                per_step_candidates=30,
                controller=controller,
            )
            if region_paths is None:
                placement_ok = False
                break

            for word, path in zip(words_in_region, region_paths):
                if not path_compatible_with_existing(path, [e["path"] for e in placed_words]):
                    placement_ok = False
                    break
                place_word(grid, path, word)
                placed_words.append({
                    "word": word,
                    "path": path,
                    "type": "theme",
                    "region_idx": region_idx,
                })

            if not placement_ok:
                break

        if not placement_ok:
            continue

        if repair_ambiguities(grid, placed_words, regions, max_iterations=20, controller=controller):
            return grid, assignment

    return None, None


def build_unique_puzzle(
    spangram,
    theme_words,
    spangram_attempts=300,
    controller=None,
    spangram_mode="auto",
    long_threshold=11,
):
    for _ in range(spangram_attempts):
        if controller is not None:
            controller.check()
            controller.bump("spangram_attempts")
            controller.report()
        grid = create_grid()
        spangram_path = place_spangram(
            grid,
            spangram,
            theme_words=theme_words,
            max_attempts=1,
            controller=controller,
            spangram_mode=spangram_mode,
            long_threshold=long_threshold,
        )
        if spangram_path is None:
            continue

        solved_grid, assignment = solve_theme_words_globally(
            grid,
            spangram,
            spangram_path,
            theme_words,
            controller=controller,
        )
        if solved_grid is not None:
            return solved_grid, assignment

    return None, None


def build_fast_puzzle(
    spangram,
    theme_words,
    spangram_attempts=120,
    controller=None,
    spangram_mode="auto",
    long_threshold=11,
):
    for _ in range(spangram_attempts):
        if controller is not None:
            controller.check()
            controller.bump("spangram_attempts")
            controller.report()
        grid = create_grid()
        spangram_path = place_spangram(
            grid,
            spangram,
            theme_words=theme_words,
            max_attempts=1,
            controller=controller,
            spangram_mode=spangram_mode,
            long_threshold=long_threshold,
        )
        if spangram_path is None:
            continue

        solved_grid, assignment = solve_theme_words_fast(
            grid,
            spangram,
            spangram_path,
            theme_words,
            controller=controller,
        )
        if solved_grid is not None:
            return solved_grid, assignment

    return None, None


if __name__ == "__main__":
    # spangram = "ELECTRICITY"
    # theme_words = ["CIRCUIT", "WATTAGE", "BATTERY", "GENERATOR", "VOLTAGE"]
    # spangram = "PROCRASTINATE"
    # theme_words = ["DELAY", "DITHER", "STALL", "PAUSE", "LOITER", "HESITATE"]
    # spangram = "AUTOMOBILE"
    # theme_words = ["ENGINE", "PISTON", "CLUTCH", "CHASSIS", "GASKET", "EXHAUST"]
    # spangram = "YOGAPOSES"
    # theme_words = ["COBRA", "PLANK", "WARRIOR", "BRIDGE", "MOUNTAIN", "TRIANGLE"]
    # spangram = "THEATRICAL"
    # theme_words = ["DIALOGUE", "COSTUME", "PROPS", "SPOTLIGHT", "REHEARSAL"]
    # spangram = "MOUNTAINEER"
    # theme_words = ["SUMMIT", "CREVASSE", "GLACIER", "SHELTER", "CARABINER"]
    # spangram = "FURNITURE"
    # theme_words = ["OTTOMAN", "RECLINER", "ARMOIRE", "SIDEBOARD", "CREDENZA"]
    # spangram = "CONSTRUCTION"
    # theme_words = ["SCAFFOLD", "GIRDER", "CEMENT", "DERRICK", "BULLDOZER"]
    # spangram = "POKERHAND"
    # theme_words = ["FLUSH", "FULLHOUSE", "ROYAL", "PAIR", "QUADS", "TRIPS", "DEALER"]

    spangram = "NOCTURNAL"
    theme_words = ["BADGER", "RACCOON", "FIREFLY", "CRICKET", "OPOSSUM", "LEMUR"]

    max_seconds = int(os.getenv("STRANDS_MAX_SECONDS", "1200"))
    spangram_attempts = int(os.getenv("STRANDS_SPANGRAM_ATTEMPTS", "250"))
    progress_every = float(os.getenv("STRANDS_PROGRESS_EVERY", "10"))
    mode = os.getenv("STRANDS_MODE", "fast").strip().lower()
    spangram_mode = os.getenv("STRANDS_SPANGRAM_MODE", "auto").strip().lower()
    long_threshold = int(os.getenv("STRANDS_LONG_SPANGRAM_THRESHOLD", "11"))

    controller = SearchController(
        max_seconds=max_seconds,
        progress_every_seconds=progress_every,
    )

    try:
        if mode == "strict":
            grid, assignment = build_unique_puzzle(
                spangram,
                theme_words,
                spangram_attempts=spangram_attempts,
                controller=controller,
                spangram_mode=spangram_mode,
                long_threshold=long_threshold,
            )
        else:
            grid, assignment = build_fast_puzzle(
                spangram,
                theme_words,
                spangram_attempts=min(spangram_attempts, 160),
                controller=controller,
                spangram_mode=spangram_mode,
                long_threshold=long_threshold,
            )
    except SearchTimeout:
        grid, assignment = None, None
        print(f"Stopped after reaching time budget of {max_seconds}s")
        controller.report(force=True, context="timeout")

    if grid is None:
        print("Failed to generate a globally unique puzzle with non-overlapping paths")
    else:
        print("Successfully generated globally unique puzzle")
        print(f"Word-to-region assignment: {[len(words) for words in assignment]} words per region")
        print("\nFinal puzzle:")
        print_grid(grid)

    controller.report(force=True, context="final")

