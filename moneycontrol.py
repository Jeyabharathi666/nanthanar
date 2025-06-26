from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "mons"

def scrape_moneycontrol():
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("🌐 Navigating to the Stock Ideas page...")
            # ✅ No more load wait, just domcontentloaded
            page.goto(URL, wait_until="domcontentloaded", timeout=150000)
            print("✅ DOM content loaded. Waiting for page to render fully...")
            page.wait_for_timeout(7000)  # give time for JS to load cards

            cards = page.query_selector_all("div.InfoCardsSec_web_stckCard__X8CAV")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price", "Research"]
            rows = []

            for card in cards:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    if (el := card.query_selector("p.InfoCardsSec_web_recoTxt___V6m0 span")): date = el.inner_text().strip()
                    if (el := card.query_selector("h3 a")): name = el.inner_text().strip()
                    if (el := card.query_selector("div.InfoCardsSec_web_buy__0pluJ")): action = el.inner_text().strip()
                    if (el := card.query_selector("ul li:nth-child(1) span")): reco_price = el.inner_text().strip()
                    if (el := card.query_selector("ul li:nth-child(2) span")): target = el.inner_text().strip()
                    if (el := card.query_selector("ul li:nth-child(3) span")): current_return = el.inner_text().strip()
                    if (el := card.query_selector("a.InfoCardsSec_web_pdfBtn__LQ71I p")): research = el.inner_text().strip()


                    row = [date, name, action, target, current_return, reco_price, research]
                    if any(f != "N/A" for f in row):
                        rows.append(row)

                except Exception as card_err:
                    print(f"⚠️ Failed to parse a card: {card_err}")

            print(f"📝 Prepared {len(rows)} rows for Google Sheets.")

            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
            ts = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [ts])

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_moneycontrol()
print("stocks")



