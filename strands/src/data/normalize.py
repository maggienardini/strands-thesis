import json
import string
from datetime import datetime

INPUT_FILE = "strands_archive.json"
OUTPUT_FILE = "strands_archive_normalized.json"


def clean_spangram(spangram):
    # Remove spaces and punctuation, then uppercase
    cleaned = "".join(
        ch for ch in spangram
        if ch not in string.punctuation and not ch.isspace()
    )
    return cleaned.upper()


def normalize_puzzles(puzzles):
    for puzzle in puzzles:
        # --- Normalize spangram ---
        puzzle["spangram"] = clean_spangram(puzzle["spangram"])

        # --- Normalize theme words ---
        puzzle["theme_words"] = [
            word.upper() for word in puzzle["theme_words"]
        ]

        # --- Add day of week ---
        date_str = puzzle["date"]

        # Handle both YYYY-MM-DD and YYYY-M-D formats
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        puzzle["day_of_week"] = date_obj.strftime("%A")

        # --- Add total word count (theme words + spangram) ---
        puzzle["total_words"] = len(puzzle["theme_words"]) + 1

    return puzzles


def main():
    with open(INPUT_FILE, "r") as f:
        puzzles = json.load(f)

    normalized = normalize_puzzles(puzzles)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(normalized, f, indent=2)

    print(f"Normalized data written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()