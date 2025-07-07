print("📈 Business Standard Scraper Starting...")

from datetime import datetime
from playwright.sync_api import sync_playwright
import google_sheets

URL = "https://www.business-standard.com/markets/research-report"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"

def scrape_business_standard():
    print("🚀 Launching browser...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()

            # Stealth anti-bot bypass
            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)

            print(f"🌐 Navigating to {URL}...")
            page.goto(URL, timeout=60000, wait_until="networkidle")

            try:
                page.wait_for_selector("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr", timeout=20000)
                trs = page.query_selector_all("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr")
                print(f"✅ Found {len(trs)} rows in the table.")

                if not trs:
                    print("❌ No rows found.")
                    return

                # Extract data
                headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
                rows = []

                for tr in trs[:500]:
                    tds = tr.query_selector_all("td")
                    if len(tds) >= 5:
                        row = [td.inner_text().strip() for td in tds[:5]]
                        rows.append(row)

                if rows:
                    print(f"📤 Updating Google Sheet with {len(rows)} rows...")
                    google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", ts])
                    print("✅ Google Sheet update complete.")
                else:
                    print("⚠️ Table present but no rows extracted.")

            except Exception as e:
                print("❌ Table selector failed.")
                print("📛 Error:", e)

            browser.close()
            print("🧹 Browser closed.")

    except Exception as e:
        print(f"❌ Fatal browser error: {e}")

scrape_business_standard()
print("✅ Script finished.")
