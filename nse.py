import re
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from nselib import capital_market
from difflib import get_close_matches

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

# 📄 Google Sheets setup
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bt10/7"
CREDENTIALS_FILE = "pags-429207-b6b0c60cd0ce.json"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# 📥 Company names from column B (no header)
company_names = sheet.col_values(2)

# 📊 Load NSE equity list
equity_df = capital_market.equity_list()
equity_df['SYMBOL'] = equity_df['SYMBOL'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.upper()
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(
    r'\b(LTD|LIMITED|INDS|INDIA|HEALT|HEALTH|SERV|SERVICES|DEVL|DEVEL|DEVELOPERS|ENER\.IND|ENERGY|ENGG|JEWE|JEWELLERS|BANK|LINES|LINE|HOSPITALS)\b',
    '', regex=True)
equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].str.replace(r'[^A-Z0-9 ]', '', regex=True).str.strip()

# 🚀 Write NSE codes to column C (starting at row 1)
for i, name in enumerate(company_names, start=1):
    nse_code = get_nse_code(name, equity_df)
    sheet.update_acell(f"C{i}", nse_code)
    print(f"[Row {i}] {name} → {nse_code}")

print("\n✅ All NSE codes updated in column C.")
