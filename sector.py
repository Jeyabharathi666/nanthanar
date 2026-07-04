import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yfinance as yf

# === Write service account from GitHub secret ===
with open("creds.json", "w") as f:
    f.write(os.environ["NEW"])

# === Google Sheets Setup ===
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
WORKSHEET_NAME = "FLIST"
CREDENTIALS_FILE = "creds.json"
flist_sheet = client.open_by_key(SHEET_ID).worksheet("FLIST")

nt_sheet = client.open_by_key(SHEET_ID).worksheet("nt")
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# === Fetch sector from yfinance ===
_cache = {}

def get_sector(symbol):
    if not symbol or symbol.strip() in ("", "ERROR", "N/A", "-"):
        return ""

    symbol = symbol.strip().upper()

    if symbol in _cache:
        return _cache[symbol]

    try:
        info = yf.Ticker(f"{symbol}.NS").info
        sector = info.get("sector") or "Unknown"
        _cache[symbol] = sector
        return sector

    except Exception as e:
        print(f"⚠️ Failed for {symbol}: {e}")
        _cache[symbol] = "Unknown"
        return "Unknown"
# ==========================================================
# Sync NT -> FLIST
# ==========================================================

# Existing symbols in FLIST
existing_symbols = {
    s.strip().upper()
    for s in flist_sheet.col_values(2)[3:]
    if s.strip()
}

# Read complete rows from NT
nt_rows = nt_sheet.get_all_values()[3:]

rows_to_append = []

for row in nt_rows:

    if len(row) < 2:
        continue

    symbol = row[1].strip().upper()

    if symbol and symbol not in existing_symbols:

        rows_to_append.append(row)

        existing_symbols.add(symbol)

if rows_to_append:

    flist_sheet.append_rows(rows_to_append)

    print(f"✅ Added {len(rows_to_append)} new stocks to FLIST")

else:

    print("✅ FLIST already up to date")
# === Read symbols starting from B4 ===
symbols = sheet.col_values(2)[3:]   # skip first 3 rows

print(f"📋 Found {len(symbols)} symbols from B4\n")

sector_updates = []

for i, symbol in enumerate(symbols, start=4):

    symbol = symbol.strip()

    if not symbol:
        sector_updates.append([""])
        continue

    sector = get_sector(symbol)

    print(f"[Row {i}] {symbol:15} → {sector}")

    sector_updates.append([sector])

    time.sleep(0.4)

# === Write to column C starting from C4 ===
end_row = len(sector_updates) + 3

sheet.update(
    values=sector_updates,
    range_name=f"C4:C{end_row}"
)

print(f"\n✅ Sectors written to C4:C{end_row}")
