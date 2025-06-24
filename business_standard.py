'''from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from datetime import datetime
import google_sheets

# 🔹 URL to scrape
URL = "https://www.business-standard.com/markets/research-report"

# 🔹 Google Sheet info
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"  # Change if needed

def scrape_business_standard():
    print("🚀 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Apply stealth mode
            stealth_sync(page)

            # Load the URL
            page.goto(URL, wait_until="domcontentloaded")
            print("🌐 Page loaded. Extracting data...")

            page.wait_for_selector("table tbody tr", timeout=180000)

            headers = [
                "Company", "Action", "Target Price (₹)", "Broker", "Date"
            ]

            rows = []
            for i, row in enumerate(page.query_selector_all("table tbody tr")):
                if i >= 20:
                    break
                cells = [cell.inner_text().strip() for cell in row.query_selector_all("td")]
                if len(cells) >= 5:
                    rows.append([cells[0], cells[1], cells[2], cells[3], cells[4]])

            if rows:
                # Update Google Sheet by worksheet name
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

                # Append 4 empty rows followed by a timestamp row
                # col_count = len(headers)
                # for _ in range(4):
                #     google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [""] * col_count)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", timestamp])
                print(f"✅ Sheet updated successfully at {timestamp}")
            else:
                print("⚠️ No rows scraped from the table.")

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")
scrape_business_standard()'''


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
            browser = p.chromium.launch(headless=False)
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

