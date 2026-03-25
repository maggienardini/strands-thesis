import json
import string
from datetime import datetime

INPUT_FILE = "llm_long_lists.json"
OUTPUT_FILE = "llm_valid_lists.json"

# subset sum problem 
def subset_sum_words(puzzle):
    words = puzzle["theme_words"]
    target = 48 - len(puzzle["spangram"])
    n = len(words)
    lengths = [len(w) for w in words]

    # Step 1: Build DP table
    dp = [[False] * (target + 1) for _ in range(n + 1)]
    dp[0][0] = True

    # Step 2: Fill table
    for i in range(1, n + 1):
        for t in range(target + 1):
            # Don't take word i
            if dp[i - 1][t]:
                dp[i][t] = True

            # Take word i
            if t >= lengths[i - 1] and dp[i - 1][t - lengths[i - 1]]:
                dp[i][t] = True

    # If no solution
    if not dp[n][target]:
        return None

    # Step 3: Backtrack
    result = []
    t = target
    i = n

    while i > 0 and t > 0:
        # If value came from NOT taking the word
        if dp[i - 1][t]:
            i -= 1
        else:
            result.append(words[i - 1])
            t -= lengths[i - 1]
            i -= 1

    return result[::-1]  # reverse for original order

def find_word_subsets(puzzles):
    for puzzle in puzzles:
        print("Puzzle: " + puzzle["theme"])
        result = subset_sum_words(puzzle)  # Just test on the first puzzle for now
        if result:
            print(str(len(puzzle["spangram"])) + " " + puzzle["spangram"])
            for word in result:
                print(str(len(word)) + " " +word)
            puzzle["theme_words"] = result
        else:
            print("No valid combination of theme words found.")

    return puzzles

def main():
    with open(INPUT_FILE, "r") as f:
        puzzles = json.load(f)

    subsets = find_word_subsets(puzzles)
   
    with open(OUTPUT_FILE, "w") as f:
        json.dump(subsets, f, indent=2)

    # print(f"Normalized data written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()