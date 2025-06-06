from playwright.sync_api import sync_playwright
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
scrape_business_standard()
