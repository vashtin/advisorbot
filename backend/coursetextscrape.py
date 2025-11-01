# backend/coursetextscrape.py
import json
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch(url):
    """Fetch the ?view=txt version of a PSU course page."""
    try:
        txt_url = url if url.endswith("?view=txt") else url + "?view=txt"
        r = requests.get(txt_url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"⚠️  Failed to fetch {url}: {e}")
        return None


def parse_courses_from_text(soup, dept_name, dept_link):
    """Extract course data from plain-text view."""
    if not soup:
        return []

    text = soup.get_text("\n")

    # Matches like “IST 210 Organization of Data (3)” or “ACCTG 211 Financial... (4)”
    pattern = re.compile(r"([A-Z]{2,5}\s?\d{2,3})\s+([^\n]+?)\((\d+)\s*credit", re.IGNORECASE)
    matches = list(pattern.finditer(text))
    courses = []

    for i, match in enumerate(matches):
        code = match.group(1).strip()
        title = match.group(2).strip()
        credits = match.group(3).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        desc = text[start:end].strip()

        # Extract prerequisites if mentioned
        prereq_match = re.search(r"Prerequisite[s]?:\s*(.*)", desc, re.IGNORECASE)
        prereq = prereq_match.group(1).strip() if prereq_match else None

        # Clean description
        desc = re.sub(r"Prerequisite[s]?:.*", "", desc, flags=re.IGNORECASE).strip()

        courses.append({
            "department": dept_name,
            "code": code,
            "title": title,
            "credits": credits,
            "description": desc,
            "prerequisite": prereq,
            "link": dept_link
        })

    return courses


def main():
    with open("courselinks.json", "r") as f:
        departments = json.load(f)

    all_courses = []
    print(f"📘 Scraping {len(departments)} departments...\n")

    for i, d in enumerate(departments, 1):
        name, link = d["name"], d["link"]
        print(f"[{i}/{len(departments)}] 🏫 {name}")
        soup = fetch(link)
        dept_courses = parse_courses_from_text(soup, name, link)
        print(f"   ↳ Found {len(dept_courses)} courses.")
        all_courses.extend(dept_courses)

    with open("courses.json", "w") as f:
        json.dump(all_courses, f, indent=2)

    print(f"\n✅ Done! Saved {len(all_courses)} total courses to courses.json")


if __name__ == "__main__":
    main()
