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
SOURCE_SHEET = '22/7'
TARGET_SHEET = '22/7'

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
    target_ws.update('AM1:BA1', [headers])

    # Fetch and write data
    for i, code in enumerate(nse_codes):
        if not code.strip():
            continue
        print(f"🔍 Fetching data for {code} (Row {i+2})")
        row_data = [code] + fetch_screener_data(code)
        target_ws.update(f'AM{i+2}:BA{i+2}', [row_data])
        time.sleep(1.5)

    print("\n✅ Data written to 'sanjayview' sheet.")

# Run it
process_sanjayview()
'''
'''
import time
import re
import requests
from bs4 import BeautifulSoup
import gspread.utils
from gspread.exceptions import APIError
from google_sheets import get_google_credentials, authorize_google_sheets

# === CONFIG ===
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
SHEET_NAME = "22/7"
COLUMN_READ = 2         # B column
COLUMN_WRITE_START = 39 # AM column

headers = {"User-Agent": "Mozilla/5.0"}

# === CLEAN NUMERIC VALUES ===
def clean_float(value):
    try:
        clean = re.sub(r'[^\d.]', '', value.replace(',', ''))
        return float(clean) if clean else "NA"
    except:
        return "NA"

# === FETCH SCREENER DATA ===
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

        def get_clean_price():
            try:
                for li in soup.select("#top-ratios li.flex.flex-space-between"):
                    label = li.select_one("span.name")
                    value = li.select_one("span.value")
                    if label and "Current Price" in label.text:
                        return clean_float(value.text)
                return "NA"
            except:
                return "NA"

        return [
            get_text("h1"),                          # Company Name
            get_clean_price(),                      # Current Price
            get_label_value("Market Cap"),          # Market Cap
            get_label_value("P/E"),                 # P/E Ratio
            get_label_value("Book Value"),          # Book Value
            get_label_value("Dividend Yield"),      # Dividend Yield
            get_label_value("ROCE"),                # ROCE
            get_label_value("ROE"),                 # ROE
            get_label_value("Face Value"),          # Face Value
        ]
    except Exception as e:
        print(f"❌ Error fetching data for {nse_code}: {e}")
        return ["Error"] * 9

# === MAIN PROCESS ===
def process_sheet():
    creds = get_google_credentials()
    client = authorize_google_sheets(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    #print(f"📄 Reading NSE codes from column B in sheet: {SHEET_NAME}")
    codes = sheet.col_values(COLUMN_READ)[1:]  # Skip header

    for i, code in enumerate(codes, start=2):
        if not code.strip():
            continue

       # print(f"🔍 Row {i}: Fetching data for {code}")
        row_data = [code] + fetch_screener_data(code)

        try:
            cell_range = f"{gspread.utils.rowcol_to_a1(i, COLUMN_WRITE_START)}:{gspread.utils.rowcol_to_a1(i, COLUMN_WRITE_START + len(row_data) - 1)}"
            sheet.update(cell_range, [row_data])
           # print(f"✅ Row {i} written to {cell_range}")

        except APIError as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print(f"⚠️ Quota exceeded at row {i}. Waiting 30 seconds before continuing...")
                time.sleep(30)
                continue
            else:
                print(f"❌ APIError at row {i}: {e}")
                continue

        except Exception as e:
            print(f"❌ Other error at row {i}: {e}")
            continue

    print("\n✅ Finished processing all rows.")

# 🔁 Run it
if __name__ == "__main__":
    process_sheet()
'''
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time
import re
import gspread.utils
from gspread.exceptions import APIError
import os
import json

# === CONFIG ===
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
SHEET_NAME = "22/7"
COLUMN_READ = 2         # B column
COLUMN_WRITE_START = 39 # Column AM
headers = {"User-Agent": "Mozilla/5.0"}

# === LOAD CREDS FROM GITHUB SECRET ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
def get_google_credentials():
    raw_json = os.environ.get("NEW")
    if not raw_json:
        raise Exception("❌ Environment variable 'NEW' not found.")
    json_dict = json.loads(raw_json)
    return ServiceAccountCredentials.from_json_keyfile_dict(json_dict, scope)

creds = get_google_credentials()
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# === CLEAN NUMERIC VALUES ===
def clean_float(value):
    try:
        clean = re.sub(r'[^\d.]', '', value.replace(',', ''))
        return float(clean) if clean else "NA"
    except:
        return "NA"

# === FETCH SCREENER DATA ===
def fetch_screener_data(nse_code):
    url = f"https://www.screener.in/company/{nse_code}/"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        def get_label_value(label):
            for li in soup.select("#top-ratios li.flex.flex-space-between"):
                lbl = li.select_one("span.name")
                val = li.select_one("span.value")
                if lbl and label in lbl.text:
                    return clean_float(val.text)
            return "NA"

        return [
            get_label_value("Market Cap"),
            get_label_value("P/E"),
            get_label_value("Book Value"),
            get_label_value("Dividend Yield"),
            get_label_value("ROCE"),
            get_label_value("ROE"),
            get_label_value("Face Value"),
        ]
    except Exception as e:
        print(f"❌ Error fetching data for {nse_code}: {e}")
        return ["Error"] * 7

# === MAIN PROCESS ===
def process_sheet():
    print(f"📄 Reading NSE codes from column B in sheet: {SHEET_NAME}")
    codes = sheet.col_values(COLUMN_READ)[1:]  # Skip header

    for i, code in enumerate(codes, start=2):
        if not code.strip():
            continue

        print(f"🔍 Row {i}: Fetching data for {code}")
        row_data = fetch_screener_data(code)

        try:
            cell_range = f"{gspread.utils.rowcol_to_a1(i, COLUMN_WRITE_START)}:{gspread.utils.rowcol_to_a1(i, COLUMN_WRITE_START + len(row_data) - 1)}"
            sheet.update(cell_range, [row_data])
            print(f"✅ Row {i} written to {cell_range}")
        except APIError as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print(f"⚠️ Quota exceeded at row {i}. Waiting 30 seconds before continuing...")
                time.sleep(30)
                continue
            else:
                print(f"❌ APIError at row {i}: {e}")
                continue
        except Exception as e:
            print(f"❌ Other error at row {i}: {e}")
            continue

    print("\n✅ Finished processing all rows.")

# 🔁 Run
if __name__ == "__main__":
    process_sheet()
