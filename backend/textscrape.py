# backend/textscrape.py
import json, time, requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def fetch(url):
    """Fetch a URL and return its parsed HTML."""
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def main():
    # Load programs.json
    with open("programs.json", "r") as f:
        programs = json.load(f)

    results = []

    print(f"🔍 Extracting text from {len(programs)} program pages...\n")

    for p in programs:
        name = p["name"]
        link = p["link"]
        print(f"📘 {name}")
        try:
            soup = fetch(link)
            main = soup.select_one("div#content") or soup.select_one("main")
            text = main.get_text(" ", strip=True) if main else ""
            results.append({
                "name": name,
                "college": p["college"],
                "link": link,
                "text": text
            })
            print(f"   ✅ Text scraped ({len(text)} chars)")
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Failed to scrape {name}: {e}")

    with open("psutext.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Done! Saved {len(results)} program texts to psutext.json.")

if __name__ == "__main__":
    main()
