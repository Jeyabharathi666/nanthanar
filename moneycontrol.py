from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "mons"

def scrape_moneycontrol():
    print("📊 Moneycontrol Stock Ideas Scraper Starting...")
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Optional stealth script
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)

            print("🌐 Navigating to:", URL)
            page.goto(URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)  # Wait for any final JS to load

            print("📊 Waiting for cards to appear...")
            page.wait_for_selector("div.InfoCardsSec_web_stckCard__X8CAV", timeout=40000)
            cards = page.query_selector_all("div.InfoCardsSec_web_stckCard__X8CAV")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price"]
            rows = []

            for card in cards:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    # Date
                    el = card.query_selector("p.InfoCardsSec_web_recoTxt___V6m0 span")
                    if el: date = el.inner_text().strip()

                    # Name
                    el = card.query_selector("h3 a")
                    if el: name = el.inner_text().strip()

                    # Action
                    el = card.query_selector("div.InfoCardsSec_web_sell__RiuGp > div")
                    if el: action = el.inner_text().strip()

                    # Reco Price
                    el = card.query_selector("ul li:nth-child(1) span")
                    if el: reco_price = el.inner_text().strip()

                    # Target
                    el = card.query_selector("ul li:nth-child(2) span")
                    if el: target = el.inner_text().strip()

                    # Current Return
                    el = card.query_selector("ul li:nth-child(3) span")
                    if el: current_return = el.inner_text().strip()

                    row = [date, name, action, target, current_return, reco_price]
                    if any(field != "N/A" for field in row):
                        rows.append(row)

                except Exception as e:
                    print(f"⚠️ Error parsing card: {e}")
                    continue

            print(f"📝 Prepared {len(rows)} valid rows for Google Sheets.")

            # Update the sheet
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

            # Append timestamp
            timestamp = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [timestamp])

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

scrape_moneycontrol()
