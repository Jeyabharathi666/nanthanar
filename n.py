from google_sheets import update_google_sheet_by_name, append_footer
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 🔗 Target URL
url = "https://www.business-standard.com/markets/research-report"
headers = {"User-Agent": "Mozilla/5.0"}

# 🌐 Fetch and parse the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 🔍 Locate the table
table = soup.find("table", class_="cmpnydatatable_cmpnydatatable__Cnf6M")

# 🧾 Extract headers
thead = table.find("thead")
headers = [th.get_text(strip=True) for th in thead.find_all("th")]

# 📊 Extract rows
tbody = table.find("tbody")
rows = []
for tr in tbody.find_all("tr"):
    row = [td.get_text(strip=True) for td in tr.find_all("td")]
    rows.append(row)

# 🧾 Google Sheet configuration
sheet_id = "YOUR_GOOGLE_SHEET_ID"  # Replace with your actual Sheet ID
worksheet_name = "Research Reports"

# 📤 Upload to Google Sheets
update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows)

# 🕒 Append timestamp footer
timestamp = datetime.now().strftime("Last updated on %Y-%m-%d %H:%M:%S")
append_footer(sheet_id, worksheet_name, [timestamp])
