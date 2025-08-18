from playwright.sync_api import sync_playwright
import json
from google_sheets import get_google_credentials, authorize_google_sheets
import time
import gspread

# ====== CONFIG ======
COOKIE_FILE = "screener.json"
BASE_URL = "https://www.screener.in/company/"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "indpe"

xpaths = {
    "Industry PE": "/html/body/main/div[3]/div[3]/div[2]/ul/li[12]/span[2]/span",
    "FII holding": "/html/body/main/div[3]/div[3]/div[2]/ul/li[17]/span[2]/span",
    "DII holding": "/html/body/main/div[3]/div[3]/div[2]/ul/li[16]/span[2]/span",
    "Debt to equity": "/html/body/main/div[3]/div[3]/div[2]/ul/li[6]/span[2]/span",
    "Promoter holding": "/html/body/main/div[3]/div[3]/div[2]/ul/li[11]/span[2]/span"
}

# ====== HELPERS ======
def update_with_retry(worksheet, cell_range, values, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            worksheet.update(cell_range, values)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print("⚠️ Quota exceeded, waiting 30 seconds before retrying...")
                time.sleep(30)
                retries += 1
            else:
                raise
    raise Exception("Max retries exceeded for Google Sheets update due to quota limits.")

def get_text_with_wait(page, xpath, retries=10, delay=1):
    """Try to extract text from an element, waiting until it loads."""
    for _ in range(retries):
        el = page.locator(f"xpath={xpath}")
        if el.count() > 0:
            text = el.inner_text().strip()
            if text:  # not empty
                return text
        time.sleep(delay)
    return "NA"

# ====== MAIN ======
# Load cookies
with open(COOKIE_FILE, "r", encoding="utf-8") as f:
    cookies = json.load(f)

for cookie in cookies:
    if "sameSite" not in cookie or cookie["sameSite"] not in ["Strict", "Lax", "None"]:
        cookie["sameSite"] = "Lax"
    if cookie["sameSite"] == "None":
        cookie["secure"] = True

# Google Sheets connection
credentials = get_google_credentials()
gc = authorize_google_sheets(credentials)
worksheet = gc.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
rows = worksheet.get_all_values()

# Launch browser and reuse context/page for all NSE codes
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # set False for debugging
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()

    for i, row in enumerate(rows[1:], start=2):
        nse_code = row[0].strip()
        if not nse_code:
            continue

        print(f"Scraping {nse_code} (Row {i})...")

        try:
            page.goto(f"{BASE_URL}{nse_code}/", timeout=30000)

            scraped_data = []
            for name, xpath in xpaths.items():
                try:
                    value = get_text_with_wait(page, xpath, retries=10, delay=1)
                except Exception:
                    value = "NA"
                scraped_data.append(value)
                print(f"  {name}: {value}")

            update_with_retry(worksheet, f"B{i}:E{i}", [scraped_data])
            print(f"✅ Row {i} updated: {scraped_data}")

        except Exception as e:
            try:
                update_with_retry(worksheet, f"B{i}:E{i}", [["ERROR", "ERROR", "ERROR", "ERROR"]])
            except Exception as e2:
                print(f"❌ Failed to update error status for row {i}: {e2}")
            print(f"❌ Row {i} failed: {e}")

    browser.close()
