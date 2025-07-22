import requests
from datetime import datetime
from gspread.exceptions import APIError
import time
from google_sheets import get_google_credentials, authorize_google_sheets

# === CONFIG ===
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"
API_URL = "https://api.moneycontrol.com/mcapi/v1/broker-research/get-analysts-choice?start=0&limit=500&sortBy=broker_count&deviceType=W"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.moneycontrol.com/"
}

# === SETUP GOOGLE SHEETS ===
creds = get_google_credentials()
client = authorize_google_sheets(creds)

try:
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
except Exception as e:
    print(f"❌ Failed to open worksheet: {e}")
    exit(1)

# === FETCH ANALYST CHOICE DATA ===
try:
    resp = requests.get(API_URL, headers=headers, timeout=10)
    data = resp.json()
    stock_ideas = data.get("data", [])
    print(f"✅ Fetched {len(stock_ideas)} stock ideas.\n")
except Exception as e:
    print(f"❌ API fetch failed: {e}")
    stock_ideas = []

# === PREPARE DATA ===
rows = [["Stock", "Analysts", "Buys", "Holds", "CMP", "Low (₹)", "Low (%)", "Avg (₹)", "Avg (%)", "High (₹)", "High (%)"]]

for idea in stock_ideas:
    try:
        name = idea.get("stkname", "N/A")
        analysts = idea.get("broker_count", "N/A")
        buys = idea.get("buy_count", "N/A")
        holds = idea.get("hold_count", "N/A")
        cmp = idea.get("cmp", "N/A")

        # Initialize target values
        low_val = avg_val = high_val = "N/A"
        low_pct = avg_pct = high_pct = "N/A"

        for target in idea.get("targets", []):
            if target["id"] == "min_target_price":
                low_val = target.get("value", "N/A")
                low_pct = target.get("percentages", "N/A") or "N/A"
            elif target["id"] == "avg_target_price":
                avg_val = target.get("value", "N/A")
                avg_pct = target.get("percentages", "N/A") or "N/A"
            elif target["id"] == "max_target_price":
                high_val = target.get("value", "N/A")
                high_pct = target.get("percentages", "N/A") or "N/A"

        rows.append([name, analysts, buys, holds, cmp, low_val, low_pct, avg_val, avg_pct, high_val, high_pct])
    except Exception as e:
        print(f"⚠️ Error parsing idea: {e}")
        continue

# === ADD TIMESTAMP FOOTER ===
timestamp = datetime.now().strftime("Updated on %d-%m-%Y at %I:%M %p")
rows.append([""] * 10 + [timestamp])  # put timestamp in last column

# === UPLOAD TO SHEET WITH QUOTA CHECK ===
try:
    print(f"📤 Uploading to Google Sheet '{WORKSHEET_NAME}'...")
    sheet.clear()
    sheet.update("A1", rows)
    print(f"✅ Uploaded {len(rows)-2} stock ideas successfully. Timestamp: {timestamp}")
except APIError as e:
    if "quota" in str(e).lower() or "429" in str(e):
        print("⚠️ Quota exceeded. Waiting 30 seconds and retrying...")
        time.sleep(30)
        try:
            sheet.clear()
            sheet.update("A1", rows)
            print(f"✅ Retried and uploaded successfully. Timestamp: {timestamp}")
        except Exception as e2:
            print(f"❌ Upload failed again after wait: {e2}")
    else:
        print(f"❌ Google Sheets API error: {e}")
except Exception as e:
    print(f"❌ Other error while uploading: {e}")

'''

import requests
from datetime import datetime
from gspread.exceptions import APIError
import time
from google_sheets import get_google_credentials, authorize_google_sheets

# === CONFIG ===
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"
API_URL = "https://api.moneycontrol.com/mcapi/v1/broker-research/get-analysts-choice?start=0&limit=500&sortBy=broker_count&deviceType=W"

# === HEADERS ===
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.moneycontrol.com/"
}

# === SETUP GOOGLE SHEETS ===
creds = get_google_credentials()
client = authorize_google_sheets(creds)

try:
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
except Exception as e:
    print(f"❌ Failed to open worksheet: {e}")
    exit(1)

# === FETCH ANALYST CHOICE DATA ===
try:
    resp = requests.get(API_URL, headers=headers, timeout=10)
    data = resp.json()
    stock_ideas = data.get("data", [])
    print(f"✅ Fetched {len(stock_ideas)} stock ideas.\n")
except Exception as e:
    print(f"❌ API fetch failed: {e}")
    stock_ideas = []

# === PREPARE DATA ===
rows = [["Stock", "Analysts", "Buys", "Holds", "CMP", "Low (₹ / %)", "Avg (₹ / %)", "High (₹ / %)"]]

for idea in stock_ideas:
    try:
        name = idea.get("stkname", "N/A")
        analysts = idea.get("broker_count", "N/A")
        buys = idea.get("buy_count", "N/A")
        holds = idea.get("hold_count", "N/A")
        cmp = idea.get("cmp", "N/A")

        low_val = avg_val = high_val = "N/A"
        low_pct = avg_pct = high_pct = "N/A"

        for target in idea.get("targets", []):
            if target["id"] == "min_target_price":
                low_val = target.get("value", "N/A")
                low_pct = target.get("percentages", "N/A") or "N/A"
            elif target["id"] == "avg_target_price":
                avg_val = target.get("value", "N/A")
                avg_pct = target.get("percentages", "N/A") or "N/A"
            elif target["id"] == "max_target_price":
                high_val = target.get("value", "N/A")
                high_pct = target.get("percentages", "N/A") or "N/A"

        low = f"{low_val} / {low_pct}%" if low_val != "N/A" else "N/A"
        avg = f"{avg_val} / {avg_pct}%" if avg_val != "N/A" else "N/A"
        high = f"{high_val} / {high_pct}%" if high_val != "N/A" else "N/A"

        rows.append([name, analysts, buys, holds, cmp, low, avg, high])
    except Exception as e:
        print(f"⚠️ Error parsing idea: {e}")
        continue

# === ADD TIMESTAMP FOOTER ===
timestamp = datetime.now().strftime("Updated on %d-%m-%Y at %I:%M %p")
rows.append([""] * 7 + [timestamp])

# === UPLOAD TO SHEET WITH QUOTA CHECK ===
try:
    print(f"📤 Uploading to Google Sheet '{WORKSHEET_NAME}'...")
    sheet.clear()
    sheet.update("A1", rows)
    print(f"✅ Uploaded {len(rows)-2} rows successfully. Timestamp: {timestamp}")
except APIError as e:
    if "quota" in str(e).lower() or "429" in str(e):
        print("⚠️ Quota exceeded. Waiting 30 seconds and retrying...")
        time.sleep(30)
        try:
            sheet.clear()
            sheet.update("A1", rows)
            print(f"✅ Retried and uploaded successfully. Timestamp: {timestamp}")
        except Exception as e2:
            print(f"❌ Upload failed again after wait: {e2}")
    else:
        print(f"❌ Google Sheets API error: {e}")
except Exception as e:
    print(f"❌ Other error while uploading: {e}")
'''
