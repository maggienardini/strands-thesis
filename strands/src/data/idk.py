import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

URL = "https://wordsrated.com/solvers/nyt-strands-archive-all-past-answers/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def parse_date(date_str):
    # "March 4, 2024" -> "2024-03-04"
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        return None

def scrape_wordsrated(start_date, end_date):
    res = requests.get(URL, headers=HEADERS, timeout=15)
    if res.status_code != 200:
        print(f"❌ Failed to fetch page: {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text("\n")
    # DEBUG - remove after fixing
    # idx = text.find("Strands March")
    # print(repr(text[idx:idx+300]))

    results = []

    # Each entry looks like:
    # Strands March 4, 2024 - Theme here
    # Theme words: WORD1, WORD2
    # Spangram: SPANGRAM
    pattern = re.compile(
        r"Strands\s+(\w+ \d+,\s*\d{4})\s*-\s*\n"   # date line
        r"\s*(.+?)\s*\n"                              # theme (next line)
        r"[\s\S]*?"                                   # anything in between
        r"Theme words\s*:\s*\n\s*(.+?)\s*\n"         # theme words
        r"[\s\S]*?"                                   # anything in between
        r"Spangram\s*:\s*\n\s*(.+?)\s*\n",           # spangram
        re.MULTILINE
    )

    for match in pattern.finditer(text):
        date_str, theme, words_str, spangram = match.groups()
        date = parse_date(date_str)
        if not date:
            continue

        # Filter to requested date range
        if not (start_date <= date <= end_date):
            continue

        theme = theme.strip()
        spangram = spangram.strip()
        theme_words = [w.strip().title() for w in words_str.split(",") if w.strip()]

        results.append({
            "date": date,
            "theme": theme,
            "spangram": spangram,
            "theme_words": theme_words,
            "source": URL
        })
        print(f"✅ {date} — theme='{theme}' spangram='{spangram}'")

    return results

def main():
    start_date = "2024-03-04"
    end_date   = "2024-12-10"

    results = scrape_wordsrated(start_date, end_date)
    results.sort(key=lambda x: x["date"], reverse=True)  # newest-first

    with open("2024_strands.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Done — {len(results)} puzzles saved")

if __name__ == "__main__":
    main()