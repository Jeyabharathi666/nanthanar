import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright
import time

SCREENER_EMAIL    = "pags40502@gmail.com"
SCREENER_PASSWORD = "Chiranjeevee1$"

GOOGLE_CREDS_FILE = "credentials.json"
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
SHEET_TAB = "nt"
DATA_START_ROW = 2

OUTPUT_HEADERS = [
    "PE", "BOKVAL", "DIVDND",
    "ROCE", "ROE", "Face",
    "INDPE", "FII", "DII", "DTE",
    "Promoters"
]

def login(page):
    page.goto("https://www.screener.in/login/")
    page.fill("input[name='username']", SCREENER_EMAIL)
    page.fill("input[name='password']", SCREENER_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url("**/dash/**")
    print("✅ Logged in")

def scrape_stock(page, symbol):

    def extract():
        data = {h: "" for h in OUTPUT_HEADERS}

        # SUMMARY
        for li in page.query_selector_all(".company-ratios li"):
            name = li.query_selector("span.name").inner_text().strip()
            val_el = li.query_selector("span.nowrap span.number, span.number")
            val = val_el.inner_text().strip() if val_el else ""

            if name == "Stock P/E":
                data["PE"] = val
            elif name == "Book Value":
                data["BOKVAL"] = val
            elif name == "Dividend Yield":
                data["DIVDND"] = val
            elif name == "ROCE":
                data["ROCE"] = val
            elif name == "ROE":
                data["ROE"] = val
            elif name == "Face Value":
                data["Face"] = val

        # TOP RATIOS
        for li in page.query_selector_all("#top-ratios li"):
            name = li.query_selector("span.name").inner_text().strip()
            val_el = li.query_selector("span.nowrap span.number, span.number")
            val = val_el.inner_text().strip() if val_el else ""

            if name == "Industry PE":
                data["INDPE"] = val
            elif name == "FII holding":
                data["FII"] = val
            elif name == "DII holding":
                data["DII"] = val
            elif name == "Debt to equity":
                data["DTE"] = val

        # PROMOTERS
        for row in page.query_selector_all("#shareholding table tr"):
            if "Promoters" in row.inner_text():
                cols = row.query_selector_all("td")
                if cols:
                    data["Promoters"] = cols[-1].inner_text().strip()
                break

        return data

    # 🔹 TRY CONSOLIDATED
    page.goto(f"https://www.screener.in/company/{symbol}/consolidated/")
    try:
        page.wait_for_selector("#top-ratios li span.name", timeout=4000)
        page.wait_for_timeout(800)
    except:
        pass

    data = extract()

    # 🔴 SIMPLE FALLBACK
    if not data["INDPE"] or data["INDPE"] == "—":
        print(f"→ fallback: {symbol}")

        page.goto(f"https://www.screener.in/company/{symbol}/")
        try:
            page.wait_for_selector("#top-ratios li span.name", timeout=4000)
            page.wait_for_timeout(800)
        except:
            pass

        data = extract()

    return data


if __name__ == "__main__":

    creds = Credentials.from_service_account_file(
        GOOGLE_CREDS_FILE,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    sheet = gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(SHEET_TAB)

    symbols = [
        s.strip().upper()
        for s in sheet.col_values(2)[DATA_START_ROW - 1:]
        if s.strip()
    ]

    print(f"📋 {len(symbols)} symbols found")

    sheet.update(values=[OUTPUT_HEADERS], range_name="L1:V1")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        for i, symbol in enumerate(symbols):
            row_num = DATA_START_ROW + i
            print(f"\n[{i+1}/{len(symbols)}] {symbol}")

            try:
                data = scrape_stock(page, symbol)
            except Exception as e:
                print("ERROR:", e)
                data = {h: "" for h in OUTPUT_HEADERS}

            row_values = [data.get(h, "") for h in OUTPUT_HEADERS]

            # ✅ ROW BY ROW UPDATE
            sheet.update(
                values=[row_values],
                range_name=f"L{row_num}:V{row_num}"
            )

            print(f"✅ Row {row_num} updated")
            time.sleep(0.4)

        browser.close()

    print("\n🎉 DONE")
