'''from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "mons"  # Update if needed

def scrape_moneycontrol():
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("🌐 Navigating to the Analysts' Choice page...")
            page.goto(URL)
            page.wait_for_selector("div.InfoCardsSec_web_stckCard__X8CAV", timeout=120000)
            time.sleep(2)

            cards = page.query_selector_all("div.InfoCardsSec_web_stckCard__X8CAV")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price"]
            rows = []

            for card in cards:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    # Date
                    date_elem = card.query_selector("p.InfoCardsSec_web_recoTxt___V6m0 span")
                    if date_elem:
                        date = date_elem.inner_text().strip()

                    # Name
                    name_elem = card.query_selector("h3 a")
                    if name_elem:
                        name = name_elem.inner_text().strip()

                    # Action (e.g. Buy)
                    action_elem = card.query_selector("div.InfoCardsSec_web_sell__RiuGp > div")
                    if action_elem:
                        action = action_elem.inner_text().strip()
                        
                   

                    # Reco Price
                    reco_price_elem = card.query_selector("ul li:nth-child(1) span")
                    if reco_price_elem:
                        reco_price = reco_price_elem.inner_text().strip()

                    # Target
                    target_elem = card.query_selector("ul li:nth-child(2) span")
                    if target_elem:
                        target = target_elem.inner_text().strip()

                    # Current Return
                    return_elem = card.query_selector("ul li:nth-child(3) span")
                    if return_elem:
                        current_return = return_elem.inner_text().strip()
                        

                    row = [date, name, action, target, current_return, reco_price]
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
'''
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === IF USING GITHUB SECRET ===
SERVICE_ACCOUNT_FILE = "pags-429207-b6b0c60cd0ce.json"
with open(SERVICE_ACCOUNT_FILE, "w") as f:
    f.write(os.environ["NEW"])  # Use secret 'NEW' from GitHub Actions

# === GOOGLE SHEET CONFIG ===
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"

# === SETUP GSPREAD ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# === FETCH FROM MONEYCONTROL STOCK IDEAS API ===
url = "https://api.moneycontrol.com/mcapi/v1/broker-research/stock-ideas?start=0&limit=1000&deviceType=W"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.moneycontrol.com/"
}
resp = requests.get(url, headers=headers)
data = resp.json()
stock_ideas = data.get("data", [])

print(f"✅ Fetched {len(stock_ideas)} stock ideas.\n")

# === PREPARE DATA FOR SHEET ===
rows = [["Date", "Stock", "CMP", "Target Price", "Upside (%)", "Recommendation", "Organization", "Recommended Price", "Report PDF"]]

for idea in stock_ideas:
    row = [
        idea.get("recommend_date", "N/A"),
        idea.get("stkname", "N/A"),
        idea.get("cmp", "N/A"),
        idea.get("target_price", "N/A"),
        idea.get("potential_returns_per", "N/A"),
        idea.get("recommend_flag", "N/A"),
        idea.get("organization", "N/A"),
        idea.get("recommended_price", "N/A"),
        idea.get("attachment", "N/A")
    ]
    rows.append(row)

# === PUSH TO SHEET ===
sheet.clear()
sheet.update(values=rows, range_name="A1")
print(f"📤 Uploaded {len(rows) - 1} stock ideas to Google Sheet '{WORKSHEET_NAME}'.")
