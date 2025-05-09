'''from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg"
WORKSHEET_NAME = "monac"  # Change as needed

def scrape_moneycontrol(): 
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            page.goto(URL)
            print("🌐 Navigating to the page...")

            page.wait_for_selector("div[class*=cardFlex] > div", timeout=60000)
            time.sleep(2)

            cards = page.query_selector_all("div[class*=cardFlex] > div")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price","1","2","3","4","5","6"]
            rows = []

            for card in cards[:40]:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    date_elem = card.query_selector("p[class*=recoTxt] span")
                    if date_elem:
                        date = date_elem.inner_text().strip()

                    name_elem = card.query_selector("h3 a")
                    if name_elem:
                        name = name_elem.inner_text().strip()

                    action_elem = card.query_selector("div[class*=btnRgt] div")
                    if action_elem:
                        action = action_elem.inner_text().strip()

                    reco_price_elem = card.query_selector("ul li:nth-child(1) span")
                    if reco_price_elem:
                        reco_price = reco_price_elem.inner_text().strip()

                    target_elem = card.query_selector("ul li:nth-child(2) span")
                    if target_elem:
                        target = target_elem.inner_text().strip()

                    return_elem = card.query_selector("ul li:nth-child(3) span")
                    if return_elem:
                        current_return = return_elem.inner_text().strip()

                    row = [date, name, action, target, current_return, reco_price]

                    if any(field != "N/A" for field in row):
                        rows.append(row)
                    else:
                       # print("⚠️ Skipped card with all N/A values.")
                       continue

                except Exception as card_err:
                    print(f"⚠️ Failed to parse a card: {card_err}")
                    continue

            print(f"📝 Prepared {len(rows)} valid rows for Google Sheets.")

            # Update the sheet by name
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)

            # Append date and time at the end
            timestamp = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [timestamp])

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_moneycontrol()
'''"""
from playwright.sync_api import sync_playwright, ElementHandle
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg"
WORKSHEET_NAME = "monac"  # Change as needed

def extract_all_texts_from_card(card: ElementHandle):
    # Extract all visible text recursively from card
    texts = card.query_selector_all("xpath=descendant::*[normalize-space()]")
    return [t.inner_text().strip() for t in texts if t.inner_text().strip()]

def scrape_moneycontrol(): 
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            page.goto(URL)
            print("🌐 Navigating to the page...")

            page.wait_for_selector("div[class*=cardFlex] > div", timeout=60000)
            time.sleep(2)

            cards = page.query_selector_all("div[class*=cardFlex] > div")
            print(f"✅ Found {len(cards)} cards.")

            rows = []
            max_length = 0

            for card in cards:
                try:
                    all_texts = extract_all_texts_from_card(card)

                    if all_texts:
                        max_length = max(max_length, len(all_texts))
                        rows.append(all_texts)
                    else:
                        print("⚠️ Skipped empty card.")
                        continue

                except Exception as card_err:
                    print(f"⚠️ Failed to parse a card: {card_err}")
                    continue

            print(f"📝 Prepared {len(rows)} valid rows for Google Sheets.")

            # Create dynamic headers based on the max number of fields
            headers = [f"Field {i+1}" for i in range(max_length)]

            # Pad rows to match header length
            padded_rows = [row + [""] * (max_length - len(row)) for row in rows]

            # Update the sheet by name
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, padded_rows)

            # Append date and time at the end
            timestamp = datetime.now().strftime("Last updated: %Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, [timestamp])

            browser.close()

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_moneycontrol()
"""
from playwright.sync_api import sync_playwright
import google_sheets
from datetime import datetime
import time

URL = "https://www.moneycontrol.com/markets/stock-ideas/analysts-choice/"
SHEET_ID = "1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg"
WORKSHEET_NAME = "MoneyControl"

def scrape_moneycontrol():
    print("🔄 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print("🌐 Navigating to the Analysts' Choice page...")
            page.goto(URL, timeout=60000)

            # Wait for card to appear
            page.wait_for_selector("div.cardFlex__flex", timeout=60000)
            time.sleep(2)  # Give extra buffer for images/content to load

            cards = page.query_selector_all("div.cardFlex__flex")
            print(f"✅ Found {len(cards)} cards.")

            headers = ["Date", "Name", "Action", "Target", "Current Return", "Reco Price"]
            rows = []

            for card in cards:
                try:
                    date = name = action = target = current_return = reco_price = "N/A"

                    # Date
                    date_elem = card.query_selector("p.recoTxt span")
                    if date_elem:
                        date = date_elem.inner_text().strip()

                    # Name
                    name_elem = card.query_selector("h3 a")
                    if name_elem:
                        name = name_elem.inner_text().strip()

                    # Action
                    action_elem = card.query_selector("div.btnRgt > div")
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
