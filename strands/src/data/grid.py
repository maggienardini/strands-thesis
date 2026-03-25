ROWS = 6
COLS = 8

def create_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def print_grid(grid):
    for row in grid:
        print(" ".join(cell if cell is not None else "." for cell in row))
    print()

DIRS_8 = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]

DIRS_4 = [
    (-1, 0), (1, 0), (0, -1), (0, 1)
]

def get_neighbors(r, c, dirs):
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc

def get_forward_neighbors(r, c, orientation):
    candidates = []

    for nr, nc in get_neighbors(r, c, DIRS_8):
        if orientation == "vertical":
            # allow same row or moving DOWN, but not up
            if nr >= r:
                candidates.append((nr, nc))
        else:
            # allow same col or moving RIGHT, but not left
            if nc >= c:
                candidates.append((nr, nc))

    return candidates

from importlib.resources import path
import random

def generate_spangram_path(spangram, max_attempts=500):
    for _ in range(max_attempts):
        
        # randomly choose orientation goal
        orientation = random.choice(["vertical", "horizontal"])
        
        # choose a starting point on a relevant edge
        if orientation == "vertical":
            start = (0, random.randint(0, COLS - 1))  # top row
        else:
            start = (random.randint(0, ROWS - 1), 0)  # left column
        
        path = [start]
        visited = {start}

        while len(path) < len(spangram):
            r, c = path[-1]
            neighbors = get_forward_neighbors(r, c, orientation)
            random.shuffle(neighbors)

            moved = False
            for nr, nc in neighbors:
                if (nr, nc) not in visited:
                    path.append((nr, nc))
                    visited.add((nr, nc))
                    moved = True
                    break

            if not moved:
                break  # dead end → restart

        if len(path) == len(spangram) and satisfies_span(path, orientation):
            return path

    return None

def satisfies_span(path, orientation):
    if orientation == "vertical":
        return any(r == 0 for r, _ in path) and any(r == ROWS - 1 for r, _ in path)
    else:
        return any(c == 0 for _, c in path) and any(c == COLS - 1 for _, c in path)

def place_spangram(grid, spangram):
    path = generate_spangram_path(spangram)

    if path is None:
        return False

    for (r, c), ch in zip(path, spangram):
        grid[r][c] = ch

    return True

def place_spangram(grid, spangram, theme_words):
    for _ in range(1000):
        path = generate_spangram_path(spangram)
        if path is None:
            continue

        # place temporarily
        for (r, c), ch in zip(path, spangram):
            grid[r][c] = ch

        if is_good_spangram(grid, theme_words):
            return True  # keep it

        # undo if bad
        for r, c in path:
            grid[r][c] = None

    return False

def get_regions(grid):
    visited = set()
    regions = []

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is None and (r, c) not in visited:
                stack = [(r, c)]
                region = []

                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in visited:
                        continue

                    visited.add((cr, cc))
                    region.append((cr, cc))

                    for nr, nc in get_neighbors(cr, cc, DIRS_4):
                        if grid[nr][nc] is None:
                            stack.append((nr, nc))

                regions.append(region)

    return regions

def is_good_spangram(grid, theme_words):
    regions = get_regions(grid)
    # print("Region sizes:", [len(r) for r in regions])

    word_lengths = [len(w) for w in theme_words]
    
    if len(regions) > 3:
        return False
    
    for region in regions:
        if not can_fill_region(len(region), word_lengths):
            return False

    return True

def can_fill_region(region_size, word_lengths):
    possible = {0}

    for length in word_lengths:
        new_possible = set(possible)
        for s in possible:
            if s + length <= region_size:
                new_possible.add(s + length)
        possible = new_possible

    return region_size in possible

def generate_word_paths(grid, start, word, allowed_cells):
    paths = []

    def dfs(path, i):
        if i == len(word):
            paths.append(path[:])
            return

        r, c = path[-1]

        for nr, nc in get_neighbors(r, c, DIRS_8):
            if (nr, nc) not in allowed_cells:
                continue

            if (nr, nc) not in path and (grid[nr][nc] is None or grid[nr][nc] == word[i]):
                path.append((nr, nc))
                dfs(path, i + 1)
                path.pop()

    dfs([start], 1)
    return paths

def place_word(grid, path, word):
    for (r, c), ch in zip(path, word):
        grid[r][c] = ch

def remove_word(grid, path, original_grid):
    for r, c in path:
        grid[r][c] = original_grid[r][c]

def place_words(grid, words, regions, index=0):
    if index == len(words):
        return all(cell is not None for row in grid for cell in row)

    word = words[index]

    for region in regions:
        # quick prune: skip regions that are too small
        if len(region) < len(word):
            continue

        region_set = set(region)

        for (r, c) in region:
            if grid[r][c] is not None:
                continue                

            paths = generate_word_paths(grid, (r, c), word, region_set)

            # 🔥 HUGE: limit search
            random.shuffle(paths)
            paths = paths[:40]

            for path in paths:
                snapshot = [row[:] for row in grid]

                place_word(grid, path, word)

                # 🔥 FIX 2: enforce UNIQUE path for this word
                all_paths = generate_word_paths(grid, path[0], word, region_set)[:2]

                if len(all_paths) == 0:
                    # ❌ not unique → undo and skip
                    for rr in range(ROWS):
                        for cc in range(COLS):
                            grid[rr][cc] = snapshot[rr][cc]
                    continue

                # proceed normally
                if place_words(grid, words, regions, index + 1):
                    return True

                # backtrack
                for rr in range(ROWS):
                    for cc in range(COLS):
                        grid[rr][cc] = snapshot[rr][cc]

    return False

if __name__ == "__main__":
    grid = create_grid()
    
    spangram = "BACKSEATDRIVER"

    theme_words = ["STEERING",
      "ACCELERATOR",
      "CLUTCH",
      "GEARSHIFT"]

    theme_words = sorted(theme_words, key=len, reverse=True)
    
    if not place_spangram(grid, spangram, theme_words):
        print("Failed to place spangram")
    else:
        regions = get_regions(grid)
        success = place_words(grid, theme_words, regions)

        if success:
            print("Words placed")
        else:
            print("Failed to place theme words")

        print_grid(grid)  # always show grid