'''import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time
import re
import os

# 🔐 Write GitHub Secret (NEW) to a file
SERVICE_ACCOUNT_FILE = 'service_account.json'
with open(SERVICE_ACCOUNT_FILE, 'w') as f:
    f.write(os.environ['NEW'])

# Google Sheets config
SHEET_ID = '1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA'
SHEET_NAMES = ['55abv', 'L45-55', 'L35-45', 'L25-35', 'L15-25']

# Setup credentials
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

headers = {"User-Agent": "Mozilla/5.0"}

# Clean and convert string to float
def clean_float(value):
    try:
        clean = re.sub(r'[^\d.]', '', value)
        return float(clean) if clean else "NA"
    except:
        return "NA"

# Fetch data from Screener.in
def fetch_screener_data(nse_code):
    url = f"https://www.screener.in/company/{nse_code}/"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        def get_text(selector):
            try:
                return soup.select_one(selector).text.strip()
            except:
                return "Not found"

        def get_clean_price():
            try:
                text = soup.select_one("div[class='company-info__price'] span.number").text.strip()
                return clean_float(text)
            except:
                return "NA"

        def get_label_value(label):
            try:
                item = soup.select_one(f"li:-soup-contains('{label}')")
                raw = item.select_one("span.number").text.strip() if item else ""
                return clean_float(raw)
            except:
                return "NA"

        return [
            get_text("h1"),                          # Company Name (string)
            get_clean_price(),                      # Current Price (float)
            get_label_value("Market Cap"),          # Float
            get_label_value("P/E"),                 # Float (IndPE)
            get_label_value("Book Value"),          # Float
            get_label_value("Dividend Yield"),      # Float
            get_label_value("ROCE"),                # Float
            get_label_value("ROE"),                 # Float
            get_label_value("Face Value"),          # Float
        ]
    except Exception as e:
        print(f"❌ Error fetching for {nse_code}: {e}")
        return ["Error"] * 9

# Process a single sheet
def process_sheet(sheet_name):
    print(f"\n📄 Processing sheet: {sheet_name}")
    sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    nse_codes = sheet.col_values(1)[1:]  # Skip header

    # Write headers starting from column AM (col 39)
    sheet.update_cell(1, 39, "Company Name")
    headers_list = ["Current Price", "Market Cap", "IndPE", "Book Value", "Dividend Yield", "ROCE", "ROE", "Face Value"]
    for j, header in enumerate(headers_list):
        sheet.update_cell(1, 40 + j, header)  # columns AM to AU

    for i, code in enumerate(nse_codes):
        if not code.strip():
            continue
        print(f"🔍 Fetching data for {code} in row {i+2}")
        row_data = fetch_screener_data(code)
        sheet.update(f'AM{i+2}:AU{i+2}', [row_data])
        time.sleep(1.5)  # avoid rate limiting

# Run for all sheets
for name in SHEET_NAMES:
    process_sheet(name)

print("\n✅ All sheets processed successfully.")
'''

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time
import re
import os

# 🔐 Write GitHub Secret (NEW) to a file
SERVICE_ACCOUNT_FILE = 'service_account.json'
with open(SERVICE_ACCOUNT_FILE, 'w') as f:
    f.write(os.environ['NEW'])

# Google Sheets config
SHEET_ID = '1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA'
SOURCE_SHEET = 'new'
TARGET_SHEET = 'sanjayview'

# Setup credentials
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

headers = {"User-Agent": "Mozilla/5.0"}

# Clean and convert string to float
def clean_float(value):
    try:
        clean = re.sub(r'[^\d.]', '', value.replace(',', ''))
        return float(clean) if clean else "NA"
    except:
        return "NA"

# Fetch data from Screener.in
def fetch_screener_data(nse_code):
    url = f"https://www.screener.in/company/{nse_code}/"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        def get_text(selector):
            try:
                return soup.select_one(selector).text.strip()
            except:
                return "Not found"

        def get_clean_price():
            try:
                for li in soup.select("#top-ratios li.flex.flex-space-between"):
                    label = li.select_one("span.name")
                    value = li.select_one("span.value")
                    if label and "Current Price" in label.text:
                        return clean_float(value.text)
                return "NA"
            except Exception as e:
                print(f"⚠️ Error extracting current price: {e}")
                return "NA"

        def get_label_value(label):
            try:
                for li in soup.select("#top-ratios li.flex.flex-space-between"):
                    lbl = li.select_one("span.name")
                    val = li.select_one("span.value")
                    if lbl and label in lbl.text:
                        return clean_float(val.text)
                return "NA"
            except:
                return "NA"

        return [
            get_text("h1"),                          # Company Name (string)
            get_clean_price(),                      # Current Price (float)
            get_label_value("Market Cap"),          # Float
            get_label_value("P/E"),                 # Float (IndPE)
            get_label_value("Book Value"),          # Float
            get_label_value("Dividend Yield"),      # Float
            get_label_value("ROCE"),                # Float
            get_label_value("ROE"),                 # Float
            get_label_value("Face Value"),          # Float
        ]
    except Exception as e:
        print(f"❌ Error fetching for {nse_code}: {e}")
        return ["Error"] * 9

# Main function to handle data transfer
def process_sanjayview():
    print(f"\n📄 Reading from sheet: {SOURCE_SHEET}")
    source_ws = client.open_by_key(SHEET_ID).worksheet(SOURCE_SHEET)
    nse_codes = source_ws.col_values(1)[1:]  # Skip header

    # Create or open target sheet
    ss = client.open_by_key(SHEET_ID)
    try:
        target_ws = ss.worksheet(TARGET_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        print(f"📘 Sheet '{TARGET_SHEET}' not found. Creating it...")
        target_ws = ss.add_worksheet(title=TARGET_SHEET, rows="100", cols="50")

    # Write headers
    headers = ["NSE Code", "Company Name", "Current Price", "Market Cap", "IndPE", "Book Value", "Dividend Yield", "ROCE", "ROE", "Face Value"]
    target_ws.update('A1:K1', [headers])

    # Fetch and write data
    for i, code in enumerate(nse_codes):
        if not code.strip():
            continue
        print(f"🔍 Fetching data for {code} (Row {i+2})")
        row_data = [code] + fetch_screener_data(code)
        target_ws.update(f'A{i+2}:K{i+2}', [row_data])
        time.sleep(1.5)

    print("\n✅ Data written to 'sanjayview' sheet.")

# Run it
process_sanjayview()
