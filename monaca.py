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
            page.wait_for_selector("div.AnylyticCardsSec_web_anylyticsCard__K0OB7", timeout=180000)
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

scrape_moneycontrol()'''

from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "monac"

def scrape_moneycontrol():
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print("🌐 Navigating to Analysts' Choice page...")
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            print("✅ DOM loaded. Waiting for JS content...")
            page.wait_for_timeout(4000)  # 7 sec for content to render

            cards = page.query_selector_all("div.AnylyticCardsSec_web_anylyticsCard__K0OB7")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Name", "Low", "Avg", "High", "Based", "CurrentPrice", "Buys", "Holds"]
            rows = []

            for card in cards:
                try:
                    name = low = avg = high = based = current_price = buys = hold = "N/A"

                    if (el := card.query_selector("h3 a")): name = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_red__UFsko")): low = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_blue__4Jr3R")): avg = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_green__n3Qdr")): high = el.inner_text().strip()
                    if (el := card.query_selector("div.AnylyticCardsSec_web_txtMid__ImCqe")): based = el.inner_text().strip()
                    if (el := card.query_selector("span.AnylyticCardsSec_web_txtColFour__DFRLg")): current_price = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_buyCol__o9t6I")): buys = el.inner_text().strip()
                    if (el := card.query_selector("p.AnylyticCardsSec_web_holdCol__Ec7wE")): hold = el.inner_text().strip()

                    row = [name, low, avg, high, based, current_price, buys, hold]
                    if any(f != "N/A" for f in row):
                        rows.append(row)

                except Exception as e_card:
                    print(f"⚠️ Error parsing card: {e_card}")

            print(f"📝 Prepared {len(rows)} rows.")

            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
            ts = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [ts])

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_moneycontrol()

