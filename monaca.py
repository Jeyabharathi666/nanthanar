print("📊 Analysts' Choice Scraper Starting...")

import os
from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"

def scrape_moneycontrol():
    print("🔄 Starting scraping process...")

    try:
        with sync_playwright() as p:
            is_ci = os.getenv("CI") == "true"
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"] if is_ci else []
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                locale="en-US"
            )
            page = context.new_page()

            # Stealth patch
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            """)

            print("🌐 Navigating to:", URL)
            page.goto(URL, wait_until="networkidle", timeout=60000)

            # Short buffer wait for full AJAX
            page.wait_for_timeout(3000)

            content = page.content()

            if "akamai" in content.lower() or "access denied" in content.lower():
                print("🚫 Bot protection (Akamai) detected. Exiting.")
                return

            print("✅ Page loaded. Looking for analyst cards...")

            page.wait_for_selector("div[class*='AnylyticCardsSec_web_anylyticsCard']", timeout=15000)
            cards = page.query_selector_all("div[class*='AnylyticCardsSec_web_anylyticsCard']")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Name", "Low", "Avg", "High", "Based", "CurrentPrice", "Buys", "Holds"]
            rows = []

            for card in cards:
                try:
                    name = low = avg = high = based = current_price = buys = hold = "N/A"

                    if (el := card.query_selector("h3 a")): name = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_red__UFsko")): low = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_blue__4Jr3R")): avg = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_green__n3Qdr")): high = el.inner_text().strip()
                    if (el := card.query_selector("div.AnylyticCardsSec_web_txtMid__ImCqe")): based = el.inner_text().strip()
                    if (el := card.query_selector("span.AnylyticCardsSec_web_txtColFour__DFRLg")): current_price = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_buyCol__o9t6I")): buys = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_holdCol__Ec7wE")): hold = el.inner_text().strip()

                    row = [name, low, avg, high, based, current_price, buys, hold]
                    if any(val != "N/A" for val in row):
                        rows.append(row)

                except Exception as e_card:
                    print(f"⚠️ Error parsing card: {e_card}")

            print(f"📝 Prepared {len(rows)} rows for Google Sheets...")

            if rows:
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
                ts = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [ts])
                print("✅ Sheet updated.")
            else:
                print("❌ No data rows extracted.")

            browser.close()
            print("🧹 Browser closed cleanly.")

    except Exception as e:
        print(f"❌ Script crashed: {e}")

if __name__ == "__main__":
    scrape_moneycontrol()

print("✅ Analysts' scraper completed.")

if __name__ == "__main__":
    scrape_moneycontrol()

print("analysts")
