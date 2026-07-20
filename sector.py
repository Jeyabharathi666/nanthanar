import os
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yfinance as yf

# === Write service account from GitHub secret ===
with open("creds.json", "w") as f:
    f.write(os.environ["NEW"])

# === Google Sheets Setup ===
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
WORKSHEET_NAME = "FULL"
CREDENTIALS_FILE = "creds.json"

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

# === Read symbols starting from B2 ===
symbols = sheet.col_values(2)[1:]   # skip header row 1, data starts at row 2
print(f"📋 Found {len(symbols)} symbols from B2\n")

sector_updates = []
for i, symbol in enumerate(symbols, start=2):
    symbol = symbol.strip()
    if not symbol:
        sector_updates.append([""])
        continue
    sector = get_sector(symbol)
    print(f"[Row {i}] {symbol:15} → {sector}")
    sector_updates.append([sector])
    time.sleep(0.4)

# === Write to column D starting from D2 ===
end_row = len(sector_updates) + 1
sheet.update(
    values=sector_updates,
    range_name=f"D2:D{end_row}"
)
print(f"\n✅ Sectors written to D2:D{end_row}")

# === Append IST date & time at the end ===
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
ist_now = datetime.datetime.now(IST)
timestamp_str = ist_now.strftime("%d-%b-%Y %I:%M:%S %p IST")

sheet.update(
    values=[[f"Last updated: {timestamp_str}"]],
    range_name=f"D{end_row + 1}"
)
print(f"🕒 Timestamp written to D{end_row + 1}: {timestamp_str}")
