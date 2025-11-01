# backend/linkscrape.py
import requests
from bs4 import BeautifulSoup
import json, time
from urllib.parse import urljoin

BASE = "https://bulletins.psu.edu"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ✅ Hardcoded static list of all PSU colleges
COLLEGE_URLS = [
    f"{BASE}/undergraduate/colleges/agricultural-sciences/",
    f"{BASE}/undergraduate/colleges/arts-architecture/",
    f"{BASE}/undergraduate/colleges/comm/",
    f"{BASE}/undergraduate/colleges/earth-mineral-sciences/",
    f"{BASE}/undergraduate/colleges/education/",
    f"{BASE}/undergraduate/colleges/engineering/",
    f"{BASE}/undergraduate/colleges/health-human-development/",
    f"{BASE}/undergraduate/colleges/information-sciences-technology/",
    f"{BASE}/undergraduate/colleges/liberal-arts/",
    f"{BASE}/undergraduate/colleges/nursing/",
    f"{BASE}/undergraduate/colleges/smeal-business/",
    f"{BASE}/undergraduate/colleges/ems-energy/",
    f"{BASE}/undergraduate/colleges/arts-letters/",
    f"{BASE}/undergraduate/colleges/eberly-science/"
]

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def get_majors_from_college(college_url):
    """Scrape one college page for bachelor program links."""
    soup = fetch(college_url)
    majors = []
    college_name = college_url.split("/")[-2].replace("-", " ").title()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if not text or not href:
            continue

        if "/undergraduate/colleges/" in href and (
            href.lower().endswith("bs/") or
            href.lower().endswith("ba/") or
            href.lower().endswith("bfa/") or
            href.lower().endswith("bmus/") or
            href.lower().endswith("bnurs/")
        ):
            majors.append({
                "name": text,
                "link": urljoin(BASE, href),
                "college": college_name
            })
    return majors

def main():
    print("🔍 Scraping Penn State colleges (static list)...")

    all_majors = []
    seen = set()

    for col_url in COLLEGE_URLS:
        print(f"\n📘 Scraping {col_url}")
        try:
            majors = get_majors_from_college(col_url)
            print(f"   ↳ Found {len(majors)} majors.")
            for m in majors:
                if m["link"] not in seen:
                    seen.add(m["link"])
                    all_majors.append(m)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  Error scraping {col_url}: {e}")

    with open("programs.json", "w") as f:
        json.dump(all_majors, f, indent=2)

    print(f"\n✅ Done! Saved {len(all_majors)} majors to programs.json")

if __name__ == "__main__":
    main()
