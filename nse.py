'''
import os
import re
import time
import pandas as pd
import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials
from nselib import capital_market
from difflib import get_close_matches

# 🔐 Write service account JSON from GitHub secret
with open("creds.json", "w") as f:
    f.write(os.environ["NEW"])

# 📄 Google Sheets setup
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
WORKSHEET_NAME = "22/7"
CREDENTIALS_FILE = "creds.json"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# 🧹 Normalize input
def normalize_input(name):
    name = name.upper()
    name = re.sub(r'\b(LTD|LIMITED|INDS|INDIA|HEALT|HEALTH|SERV|SERVICES|DEVL|DEVEL|DEVELOPERS|ENER\.IND|ENERGY|ENGG|JEWE|JEWELLERS|BANK|LINES|LINE|HOSPITALS)\b', '', name)
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# 🔍 Matching logic
def get_nse_code(user_input, df):
    try:
        input_normalized = normalize_input(user_input)

        # 1. Exact symbol match
        exact_symbol = df[df['SYMBOL'] == input_normalized]
        if not exact_symbol.empty:
            return exact_symbol.iloc[0]['SYMBOL']

        # 2. Partial name match
        partial_name = df[df['NAME OF COMPANY'].str.contains(input_normalized)]
        if not partial_name.empty:
            return partial_name.iloc[0]['SYMBOL']

        # 3. Loose symbol match
        loose_symbol = df[df['SYMBOL'].str.contains(input_normalized.replace(" ", ""))]
        if not loose_symbol.empty:
            return loose_symbol.iloc[0]['SYMBOL']

        # 4. Fuzzy match
        all_names = df['NAME OF COMPANY'].tolist()
        match = get_close_matches(input_normalized, all_names, n=1, cutoff=0.65)
        if match:
            row = df[df['NAME OF COMPANY'] == match[0]]
            return row.iloc[0]['SYMBOL']

        return "Not Found"
    except Exception as e:
        return f"Error: {e}"

# 📥 Company names from column A (no header)
company_names = sheet.col_values(1)

# 📊 Load NSE equity list
equity_df = capital_market.equity_list()
equity_df['SYMBOL'] = equity_df['SYMBOL'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(
    r'\b(LTD|LIMITED|INDS|INDIA|HEALT|HEALTH|SERV|SERVICES|DEVL|DEVEL|DEVELOPERS|ENER\.IND|ENERGY|ENGG|JEWE|JEWELLERS|BANK|LINES|LINE|HOSPITALS)\b',
    '', regex=True)
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

# 🚀 Write NSE codes to column B (starting at row 1)
for i, name in enumerate(company_names, start=1):
    try:
        nse_code = get_nse_code(name, equity_df)

        try:
            sheet.update_acell(f"B{i}", nse_code)
        except APIError as e:
            if "Quota exceeded" in str(e) or "429" in str(e):
                print(f"⚠️ Quota exceeded at Row {i}! Waiting 100 seconds...")
                time.sleep(100)
                try:
                    sheet.update_acell(f"B{i}", nse_code)
                except APIError as e2:
                    print(f"❌ Still failed at Row {i} after retry: {e2}")
            else:
                print(f"❌ API error at Row {i}: {e}")

    except Exception as ex:
        print(f"❌ Error processing Row {i}: {ex}")

# 📝 Update NSE_LIST sheet
try:
    nse_ws = client.open_by_key(SHEET_ID).worksheet("NSE_LIST")
    nse_ws.clear()
except gspread.exceptions.WorksheetNotFound:
    nse_ws = client.open_by_key(SHEET_ID).add_worksheet(title="NSE_LIST", rows="2000", cols="2")

nse_ws.update([['SYMBOL', 'NAME OF COMPANY']] + equity_df[['SYMBOL', 'NAME OF COMPANY']].values.tolist())

print("\n✅ NSE codes written to column B and NSE_LIST updated.")
'''


import os
import re
import time
import pandas as pd
import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials
from nselib import capital_market
from difflib import get_close_matches

# 🔐 Write service account JSON from GitHub secret
with open("creds.json", "w") as f:
    f.write(os.environ["NEW"])

# 📄 Google Sheets setup
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
WORKSHEET_NAME = "22/7"
CREDENTIALS_FILE = "creds.json"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# 🧹 Normalize input
def normalize_input(name):
    name = name.upper()
    name = re.sub(r'\b(LTD|LIMITED|INDS|INDIA|HEALT|HEALTH|SERV|SERVICES|DEVL|DEVEL|DEVELOPERS|ENER\.IND|ENERGY|ENGG|JEWE|JEWELLERS|BANK|LINES|LINE|HOSPITALS)\b', '', name)
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# 🔍 Matching logic with skip for bad inputs
def get_nse_code(user_input, df):
    try:
        # Skip meaningless inputs like '-', '.', empty, etc.
        if not user_input or re.fullmatch(r'[-. ]+', user_input.strip()):
            return ""

        input_normalized = normalize_input(user_input)
        if not input_normalized or len(input_normalized) < 2:
            return ""

        # 1. Exact symbol match
        exact_symbol = df[df['SYMBOL'] == input_normalized]
        if not exact_symbol.empty:
            return exact_symbol.iloc[0]['SYMBOL']

        # 2. Partial name match
        partial_name = df[df['NAME OF COMPANY'].str.contains(input_normalized)]
        if not partial_name.empty:
            return partial_name.iloc[0]['SYMBOL']

        # 3. Loose symbol match
        loose_symbol = df[df['SYMBOL'].str.contains(input_normalized.replace(" ", ""))]
        if not loose_symbol.empty:
            return loose_symbol.iloc[0]['SYMBOL']

        # 4. Fuzzy match
        all_names = df['NAME OF COMPANY'].tolist()
        match = get_close_matches(input_normalized, all_names, n=1, cutoff=0.65)
        if match:
            row = df[df['NAME OF COMPANY'] == match[0]]
            return row.iloc[0]['SYMBOL']

        return "Not Found"
    except Exception as e:
        return f"Error: {e}"

# 📥 Company names from column A (no header)
company_names = sheet.col_values(1)

# 📊 Load NSE equity list
equity_df = capital_market.equity_list()
equity_df['SYMBOL'] = equity_df['SYMBOL'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(
    r'\b(LTD|LIMITED|INDS|INDIA|HEALT|HEALTH|SERV|SERVICES|DEVL|DEVEL|DEVELOPERS|ENER\.IND|ENERGY|ENGG|JEWE|JEWELLERS|BANK|LINES|LINE|HOSPITALS)\b',
    '', regex=True)
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

# 🚀 Write NSE codes to column B (starting at row 1)
for i, name in enumerate(company_names, start=1):
    try:
        nse_code = get_nse_code(name, equity_df)

        # Skip writing if input is junk
        if nse_code == "":
            print(f"⚠️ Skipped Row {i} - input was empty or meaningless")
            continue

        try:
            sheet.update_acell(f"B{i}", nse_code)
        except APIError as e:
            if "Quota exceeded" in str(e) or "429" in str(e):
                print(f"⚠️ Quota exceeded at Row {i}! Waiting 100 seconds...")
                time.sleep(100)
                try:
                    sheet.update_acell(f"B{i}", nse_code)
                except APIError as e2:
                    print(f"❌ Still failed at Row {i} after retry: {e2}")
            else:
                print(f"❌ API error at Row {i}: {e}")

    except Exception as ex:
        print(f"❌ Error processing Row {i}: {ex}")

# 📝 Update NSE_LIST sheet
try:
    nse_ws = client.open_by_key(SHEET_ID).worksheet("NSE_LIST")
    nse_ws.clear()
except gspread.exceptions.WorksheetNotFound:
    nse_ws = client.open_by_key(SHEET_ID).add_worksheet(title="NSE_LIST", rows="2000", cols="2")

nse_ws.update([['SYMBOL', 'NAME OF COMPANY']] + equity_df[['SYMBOL', 'NAME OF COMPANY']].values.tolist())

print("\n✅ NSE codes written to column B and NSE_LIST updated.")
