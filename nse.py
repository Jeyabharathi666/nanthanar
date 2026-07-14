import os
import re
import time
import pandas as pd
import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials
from nselib import capital_market
from rapidfuzz import fuzz, process  # Much better than difflib

# === Write service account from GitHub secret ===
with open("creds.json", "w") as f:
    f.write(os.environ["NEW"])

# === Normalize ===
STRIP_WORDS = r'\b(LTD|LIMITED|PVT|PRIVATE|PLC|INC|CORP|CORPORATION|CO)\b'

def normalize(name):
    if not name or str(name).strip() in ['-', 'NA', 'N/A', '']:
        return ""
    name = str(name).upper()
    name = re.sub(STRIP_WORDS, '', name)
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    return re.sub(r'\s+', ' ', name).strip()

def tokenize(name):
    return set(name.split())

# === Layer 1: Exact symbol match ===
def match_exact_symbol(query, df):
    sym = query.replace(" ", "")
    result = df[df['SYMBOL'] == sym]
    return result.iloc[0]['SYMBOL'] if not result.empty else None

# === Layer 2: Exact / startswith name match ===
def match_name_exact(query, df):
    result = df[df['NAME_NORM'] == query]
    if not result.empty:
        return result.iloc[0]['SYMBOL']
    result = df[df['NAME_NORM'].str.startswith(query)]
    return result.iloc[0]['SYMBOL'] if not result.empty else None

# === Layer 3: Token overlap (handles word-order variation) ===
def match_token_overlap(query, df, threshold=0.75):
    query_tokens = tokenize(query)
    if not query_tokens:
        return None
    best_score, best_symbol = 0, None
    for _, row in df.iterrows():
        row_tokens = tokenize(row['NAME_NORM'])
        if not row_tokens:
            continue
        overlap = len(query_tokens & row_tokens) / max(len(query_tokens), len(row_tokens))
        if overlap > best_score:
            best_score = overlap
            best_symbol = row['SYMBOL']
    return best_symbol if best_score >= threshold else None

# === Layer 4: RapidFuzz fuzzy match (much better than difflib) ===
def match_fuzzy(query, df, cutoff=80):
    names = df['NAME_NORM'].tolist()
    # Uses token_sort_ratio to handle word order differences
    result = process.extractOne(
        query, names,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=cutoff
    )
    if result:
        match_name, score, _ = result
        row = df[df['NAME_NORM'] == match_name]
        print(f"    Fuzzy match: '{match_name}' (score={score})")
        return row.iloc[0]['SYMBOL'] if not row.empty else None
    return None

# === Master lookup ===
def get_nse_code(user_input, df):
    query = normalize(user_input)
    if not query or len(query) < 2:
        return ""

    result = (
        match_exact_symbol(query, df)
        or match_name_exact(query, df)
        or match_token_overlap(query, df, threshold=0.75)
        or match_fuzzy(query, df, cutoff=75)
        or ""
    )
    return result

# === Google Sheets Setup ===
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
WORKSHEET_NAME = "FULL"
CREDENTIALS_FILE = "creds.json"

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# === Load & pre-process NSE Equity List ===
equity_df = capital_market.equity_list()
equity_df['SYMBOL'] = equity_df['SYMBOL'].str.upper().str.strip()
equity_df['NAME_NORM'] = (
    equity_df['NAME OF COMPANY']
    .str.upper()
    .str.replace(STRIP_WORDS, '', regex=True)
    .str.replace(r'[^A-Z0-9 ]', '', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# === Batch read + batch write (fewer API calls = faster + no rate limits) ===
company_names = sheet.col_values(1)[1:]
updates = []  # Collect all updates, write in one batch

for i, name in enumerate(company_names, start=1):
    try:
        nse_code = get_nse_code(name, equity_df)
        print(f"[Row {i}] '{name}' → '{nse_code}'")
        updates.append([nse_code])
    except Exception as e:
        print(f"❌ Error at row {i} ({name}): {e}")
        updates.append(["ERROR"])

# === Single batch write to column B (avoids rate limiting) ===
if updates:
    sheet.update("B1", [["NSE Symbol"]])
    sheet.update(f"B1:B{len(updates)+1}", updates)
    print(f"\n✅ Written {len(updates)} rows to column B in one batch.")

# === Update NSE_LIST sheet ===
try:
    nse_ws = client.open_by_key(SHEET_ID).worksheet("NSE_LIST")
    nse_ws.clear()
except gspread.exceptions.WorksheetNotFound:
    nse_ws = client.open_by_key(SHEET_ID).add_worksheet(title="NSE_LIST", rows="2000", cols="3")

nse_ws.update(
    [['SYMBOL', 'ORIGINAL NAME', 'NORMALIZED NAME']] +
    equity_df[['SYMBOL', 'NAME OF COMPANY', 'NAME_NORM']].values.tolist()
)
print("✅ NSE_LIST updated with normalized names for debugging.")
