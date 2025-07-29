
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
            #get_label_value("Market Cap"),
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
COLUMN_READ = 2         # Column B (NSE codes)
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
        clean = re.sub(r'[^\d.-]', '', value.replace(',', ''))
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

        def get_promoter_pledged():
            try:
                data = soup.select_one("#shareholding .promoter").text
                match = re.search(r'Pledged.*?(\d+\.?\d*)%', data)
                return float(match.group(1)) if match else "NA"
            except:
                return "NA"

        def get_cmp():
            try:
                return clean_float(soup.select_one("#stock-overview .number").text)
            except:
                return "NA"

        def get_fcf_values():
            try:
                section = soup.find("section", id="cash-flow")
                table = section.find("table")
                rows = table.find_all("tr")
                for row in rows:
                    if "Free Cash Flow" in row.text:
                        values = [clean_float(td.text) for td in row.find_all("td")[1:]]
                        return values[:2] + ["NA"] * (2 - len(values))  # latest + previous
                return ["NA", "NA"]
            except:
                return ["NA", "NA"]

        return [
            get_label_value("P/E"),
            get_label_value("Book Value"),
            get_label_value("Dividend Yield"),
            get_label_value("ROCE"),
            get_label_value("ROE"),
            get_label_value("Face Value"),
            get_promoter_pledged(),
            get_cmp(),
            *get_fcf_values(),
            get_label_value("Debt to equity"),
        ]
    except Exception as e:
        print(f"❌ Error fetching data for {nse_code}: {e}")
        return ["Error"] * 11

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
