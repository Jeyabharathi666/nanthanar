import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Import your existing Google Sheets helpers
from google_sheets import (
    update_google_sheet_by_name,
    append_footer
)

SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "news"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------- MONEYCONTROL ----------
MC_BASE = "https://www.moneycontrol.com/news/business/stocks/page-{}/"

def fetch_moneycontrol_titles(pages=5):
    titles = []

    for page in range(1, pages + 1):
        url = MC_BASE.format(page)
        print(f"Fetching Moneycontrol page {page}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print("Moneycontrol error:", e)
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select("li.clearfix h2 a"):
            title = a.get_text(strip=True)
            if title:
                titles.append(title)

    return titles


# ---------- ECONOMIC TIMES ----------
ET_URL = "https://economictimes.indiatimes.com/markets/stocks/news"

def fetch_economictimes_titles():
    titles = []
    print("Fetching Economic Times")

    try:
        r = requests.get(ET_URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print("Economic Times error:", e)
        return titles

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")

        if (
            text
            and "/markets/stocks/news/" in href
            and len(text) > 30
        ):
            titles.append(text)

    return titles


# ---------- MAIN ----------
def main():
    mc_titles = fetch_moneycontrol_titles(pages=5)
    et_titles = fetch_economictimes_titles()

    # Combine + remove duplicates
    all_titles = list(dict.fromkeys(mc_titles + et_titles))

    rows = [[title] for title in all_titles]

    headers = ["News Title"]

    update_google_sheet_by_name(
        sheet_id=SHEET_ID,
        worksheet_name=WORKSHEET_NAME,
        headers=headers,
        rows=rows
    )

    footer = [f"Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"]
    append_footer(SHEET_ID, WORKSHEET_NAME, footer)


if __name__ == "__main__":
    main()
