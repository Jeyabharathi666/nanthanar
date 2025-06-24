from datetime import datetime
from playwright.sync_api import sync_playwright
import google_sheets

URL = "https://www.business-standard.com/markets/research-report"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"

def scrape_business_standard():
    print("🚀 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()

            # GO TO PAGE without networkidle
            page.goto(URL, timeout=60000)  # Allow up to 60s if slow network
            print("🌐 Page requested. Waiting fixed time for content...")
            page.wait_for_timeout(10_000)  # 10 seconds fixed wait

            # SCRAPE
            trs = page.query_selector_all("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr")

            if not trs:
                print("⚠️ No table rows found. Saving screenshot...")
                page.screenshot(path="final_debug.png")
                print("📸 Saved final_debug.png. Check it.")
                browser.close()
                return

            headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
            rows = []

            for tr in trs[:500]:
                tds = tr.query_selector_all("td")
                if len(tds) >= 5:
                    rows.append([td.inner_text().strip() for td in tds[:5]])

            if rows:
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", ts])
                print(f"✅ Successfully updated {len(rows)} rows.")
            else:
                print("⚠️ Table found but no rows extracted.")

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

scrape_business_standard()
print("business standard completed")
