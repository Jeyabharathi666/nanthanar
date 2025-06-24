from datetime import datetime
from playwright.sync_api import sync_playwright
import google_sheets  # Uses your provided google_sheets.py

# 🔹 URL and Google Sheet Info
URL = "https://trendlyne.com/research-reports/buy/"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "trend"  # Change this if you use a different name

def scrape_trend():
    print("🚀 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Load the page
            page.goto(URL)
            print("🌐 Page loaded. Extracting data...")

            # Wait for the table
            page.wait_for_selector("table")

            # Define headers
            headers = [
                "DATE", "STOCK", "AUTHOR", "LTP", "TARGET",
                "PRICE AT RECO (CHANGE SINCE RECO%)", "UPSIDE(%)", "TYPE"
            ]

            # Scrape rows
            rows = []
            for row in page.query_selector_all("table tbody tr"):
                cells = [cell.inner_text().strip() for cell in row.query_selector_all("td")]
                if len(cells) >= 9:
                    rows.append([cells[1], cells[2], cells[3], cells[4], cells[5], cells[6], cells[7], cells[8]])

            if rows:
                # Update the sheet by worksheet name
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

                # Append footer with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", timestamp])
            else:
                print("⚠️ No data rows found on the webpage.")

            browser.close()

    except Exception as e:
        print(f"❌ Error during scraping or sheet update: {e}")
scrape_trend()
print("trend")
