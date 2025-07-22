'''from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"  # Update if needed

def scrape_moneycontrol():
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("🌐 Navigating to the Analysts' Choice page...")
            page.goto(URL)
            page.wait_for_selector("div.AnylyticCardsSec_web_anylyticsCard__K0OB7", timeout=120000)
            time.sleep(2)

            cards = page.query_selector_all("div.AnylyticCardsSec_web_anylyticsCard__K0OB7")
            print(f"✅ Found {len(cards)} cards.")

            headers = [ "Name", "low","avg","high","based","currentPrice","Buys","Holds"]
            rows = []

            for card in cards:
                try:
                    name = buys=based=low=high=avg = hold  = current_price = "N/A"

                    

                    # Name
                    name_elem = card.query_selector("h3 a")
                    if name_elem:
                        name = name_elem.inner_text().strip()
                         # low
                    low_elem = card.query_selector("p.AnylyticCardsSec_web_red__UFsko")
                    if low_elem:
                        low = low_elem.inner_text().strip()
                        # avg
                    avg_elem = card.query_selector("p.AnylyticCardsSec_web_blue__4Jr3R")
                    if avg_elem:
                        avg = avg_elem.inner_text().strip()
                         # high
                    high_elem = card.query_selector("p.AnylyticCardsSec_web_green__n3Qdr")
                    if high_elem:
                        high = high_elem.inner_text().strip()
 # based
                    based_elem = card.query_selector("div.AnylyticCardsSec_web_txtMid__ImCqe")
                    if based_elem:
                        based = based_elem.inner_text().strip()

                    # buys (e.g. Buy)
                    buys_elem = card.query_selector("p.AnylyticCardsSec_web_buyCol__o9t6I")
                    if buys_elem:
                        buys = buys_elem.inner_text().strip()
                        # buys (e.g. Buy)
                    hold_elem = card.query_selector("p.AnylyticCardsSec_web_holdCol__Ec7wE")
                    if hold_elem:
                        hold = hold_elem.inner_text().strip()

                    # Reco Price
                    current_price_elem = card.query_selector("span.AnylyticCardsSec_web_txtColFour__DFRLg")
                    if current_price_elem:
                        current_price = current_price_elem.inner_text().strip()
                        
                  

                  
                    row = [ name,low,avg,high ,based, current_price,buys,hold]
                    if any(field != "N/A" for field in row):
                        rows.append(row)

                except Exception as card_err:
                    print(f"⚠️ Failed to parse a card: {card_err}")
                    continue

            print(f"📝 Prepared {len(rows)} valid rows for Google Sheets.")

            # Update the sheet
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

            # Append timestamp
            timestamp = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [timestamp])

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_moneycontrol()

if __name__ == "__main__":
    scrape_moneycontrol()

print("analysts")

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === CONFIG ===
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"
SERVICE_ACCOUNT_FILE = "pags-429207-b6b0c60cd0ce.json"

# === SETUP GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# === FETCH ANALYST CHOICE DATA ===
url = "https://api.moneycontrol.com/mcapi/v1/broker-research/get-analysts-choice?start=0&limit=500&sortBy=broker_count&deviceType=W"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.moneycontrol.com/"
}
resp = requests.get(url, headers=headers)
data = resp.json()
stock_ideas = data.get("data", [])

print(f"✅ Fetched {len(stock_ideas)} stock ideas.\n")

# === PREPARE DATA FOR GSheet ===
rows = [["Stock", "Analysts", "Buys", "Holds", "CMP", "Low (₹ / %)", "Avg (₹ / %)", "High (₹ / %)"]]

for idea in stock_ideas:
    try:
        name = idea.get("stkname", "N/A")
        analysts = idea.get("broker_count", "N/A")
        buys = idea.get("buy_count", "N/A")
        holds = idea.get("hold_count", "N/A")
        cmp = idea.get("cmp", "N/A")

        # Extract targets
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

        # Format values
        low = f"{low_val} / {low_pct}%" if low_val != "N/A" else "N/A"
        avg = f"{avg_val} / {avg_pct}%" if avg_val != "N/A" else "N/A"
        high = f"{high_val} / {high_pct}%" if high_val != "N/A" else "N/A"

        rows.append([name, analysts, buys, holds, cmp, low, avg, high])
    except Exception as e:
        print(f"⚠️ Error parsing stock idea: {e}")
        continue

# === APPEND TIMESTAMP AT BOTTOM ===
timestamp = datetime.now().strftime("Updated on %d-%m-%Y at %I:%M %p")
rows.append([""] * 7 + [timestamp])  # put timestamp in last column

# === WRITE TO SHEET ===
sheet.clear()
sheet.update(values=rows, range_name="A1")
print(f"📤 Uploaded {len(rows)-2} stock ideas to Google Sheet '{WORKSHEET_NAME}'. ✅ Timestamp: {timestamp}")
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
