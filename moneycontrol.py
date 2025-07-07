import os
import time
from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime

URL = "https://www.moneycontrol.com/markets/stock-ideas"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "mons"
USE_STEALTH = True  # Set to False if you want to disable stealth

def scrape_moneycontrol():
    print("📊 Moneycontrol Stock Ideas Scraper Starting...")
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            is_ci = os.getenv("CI") == "true"
            browser = p.chromium.launch(
                headless=is_ci,
                args=["--no-sandbox", "--disable-setuid-sandbox"] if is_ci else []
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()

            # Optional stealth
            if USE_STEALTH:
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                """)

            print(f"🌐 Navigating to: {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)

            print("⏳ Waiting for cards to appear...")
            page.wait_for_selector("div.InfoCardsSec_web_stckCard__X8CAV", timeout=40000)
            time.sleep(2)  # slight buffer

            cards = page.query_selector_all("div.InfoCardsSec_web_stckCard__X8CAV")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price"]
            rows = []

            for card in cards:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    if (el := card.query_selector("p.InfoCardsSec_web_recoTxt___V6m0 span")):
                        date = el.inner_text().strip()

                    if (el := card.query_selector("h3 a")):
                        name = el.inner_text().strip()

                    if (el := card.query_selector("div.InfoCardsSec_web_sell__RiuGp > div")):
                        action = el.inner_text().strip()

                    if (el := card.query_selector("ul li:nth-child(2) span")):
                        target = el.inner_text().strip()

                    if (el := card.query_selector("ul li:nth-child(3) span")):
                        current_return = el.inner_text().strip()

                    if (el := card.query_selector("ul li:nth-child(1) span")):
                        reco_price = el.inner_text().strip()

                    row = [date, name, action, target, current_return, reco_price]
                    if any(field != "N/A" for field in row):
                        rows.append(row)

                except Exception as e_card:
                    print(f"⚠️ Error parsing card: {e_card}")
                    continue

            print(f"📝 Prepared {len(rows)} rows.")

            # Push to Google Sheet
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
            ts = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [ts])
            print("✅ Sheet updated successfully.")

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    scrape_moneycontrol()
