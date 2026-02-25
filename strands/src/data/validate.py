import json

INPUT_FILE = "strands_archive_normalized.json"
EXPECTED_LETTER_COUNT = 48


def count_letters(word):
    return sum(1 for ch in word if ch.isalpha())


def validate_puzzles(puzzles):
    invalid_puzzles = []

    for puzzle in puzzles:
        total_letters = 0

        # Count spangram letters
        total_letters += count_letters(puzzle["spangram"])

        # Count theme word letters
        for word in puzzle["theme_words"]:
            total_letters += count_letters(word)

        if total_letters != EXPECTED_LETTER_COUNT:
            invalid_puzzles.append({
                "date": puzzle["date"],
                "letter_count": total_letters
            })

    return invalid_puzzles


def main():
    with open(INPUT_FILE, "r") as f:
        puzzles = json.load(f)

    invalid = validate_puzzles(puzzles)

    if not invalid:
        print("All puzzles are well formed (48 letters).")
    else:
        print("Invalid puzzles found:")
        for puzzle in invalid:
            print(
                f"Date: {puzzle['date']} "
                f"-> Letter Count: {puzzle['letter_count']}"
            )


if __name__ == "__main__":
    main()