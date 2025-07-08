from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from google_sheets import update_google_sheet_by_name, append_footer
from datetime import datetime

# Google Sheet config
sheet_id = "YOUR_GOOGLE_SHEET_ID"  # Replace with your actual Sheet ID
worksheet_name = "Research Reports"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.business-standard.com/markets/research-report", timeout=60000)
    page.wait_for_selector("table.cmpnydatatable_cmpnydatatable__Cnf6M")

    html = page.content()
    browser.close()

# Parse the rendered HTML
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", class_="cmpnydatatable_cmpnydatatable__Cnf6M")

# Extract headers
thead = table.find("thead")
headers = [th.get_text(strip=True) for th in thead.find_all("th")]

# Extract rows
tbody = table.find("tbody")
rows = []
for tr in tbody.find_all("tr"):
    row = [td.get_text(strip=True) for td in tr.find_all("td")]
    rows.append(row)

# Upload to Google Sheets
update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)

# Append timestamp
timestamp = datetime.now().strftime("Last updated on %Y-%m-%d %H:%M:%S")
append_footer(sheet_id, worksheet_name, [timestamp])
