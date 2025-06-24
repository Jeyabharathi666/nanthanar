from playwright.sync_api import sync_playwright
from datetime import datetime
import google_sheets

URL = "https://economictimes.indiatimes.com/markets/stock-recos/newrecos/buy"
sheet_id = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
worksheet_name = "eco"
def scrape_economictimes():
    print("Starting the scraping process...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL)
        print("Page loaded. Waiting for the table to be available...")

        page.wait_for_selector(".eticon_list_view.styles_listingIcon__kDghH")
        page.click(".eticon_list_view.styles_listingIcon__kDghH")

        page.wait_for_selector("#fixedTable")
        page.wait_for_selector("#scrollableTable")
        print("Tables are now visible. Extracting data...")

        headers = ["Stock Name", "Recommendation", "Potential Upside/Downside", "Target Price", "Current Price", "Price at Recos"]
        stock_name_rows = page.query_selector_all("#fixedTable tbody tr")
        scrollable_table_rows = page.query_selector_all("#scrollableTable tbody tr")

        if len(stock_name_rows) != len(scrollable_table_rows):
            print("⚠️ Row count mismatch between tables.")

        rows = []
        for i in range(min(20, len(stock_name_rows), len(scrollable_table_rows))):
            stock_name = stock_name_rows[i].query_selector("td").inner_text().strip()
            cells = scrollable_table_rows[i].query_selector_all("td")
            if len(cells) >= 5:
                recommendation = cells[0].inner_text().strip()
                potential_upside = cells[1].inner_text().strip()
                target_price = cells[2].inner_text().strip()
                current_price = cells[3].inner_text().strip()
                price_at_rec = cells[4].inner_text().strip()

                rows.append([stock_name, recommendation, potential_upside, target_price, current_price, price_at_rec])

        

        # Update sheet
        google_sheets.update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)

        # Add timestamp footer after 4 empty rows
        now = datetime.now().strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        browser.close()

scrape_economictimes()
print("economic times")
