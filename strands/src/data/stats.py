import json
import statistics

def load_data(filename):
    with open(filename, "r") as f:
        return json.load(f)

def main():
    data = load_data("strands_archive_normalized.json")  # change filename if needed

    all_word_lengths = []
    per_puzzle_variation = []
    spangram_lengths = []

    for puzzle in data:
        theme_words = puzzle.get("theme_words", [])
        spangram = puzzle.get("spangram", "")

        # Theme word lengths
        lengths = [len(word) for word in theme_words]
        all_word_lengths.extend(lengths)

        # Variation within this puzzle (std deviation)
        if len(lengths) > 1:
            variation = statistics.pstdev(lengths)
            per_puzzle_variation.append(variation)

        # Spangram length
        if spangram:
            spangram_lengths.append(len(spangram))

    # --- Stats ---
    avg_theme_word_length = statistics.mean(all_word_lengths) if all_word_lengths else 0
    avg_variation = statistics.mean(per_puzzle_variation) if per_puzzle_variation else 0

    avg_spangram_length = statistics.mean(spangram_lengths) if spangram_lengths else 0
    min_spangram_length = min(spangram_lengths) if spangram_lengths else 0
    max_spangram_length = max(spangram_lengths) if spangram_lengths else 0

    # --- Print ---
    print(f"Average theme word length: {avg_theme_word_length:.2f}")
    print(f"Average variation in theme word length (std dev): {avg_variation:.2f}")
    print(f"Average spangram length: {avg_spangram_length:.2f}")
    print(f"Min spangram length: {min_spangram_length}")
    print(f"Max spangram length: {max_spangram_length}")

if __name__ == "__main__":
    main()