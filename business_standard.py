'''print("business")
from datetime import datetime
from playwright.sync_api import sync_playwright
#from tf_playwright_stealth import stealth_sync  # Uncomment if using stealth
import google_sheets

URL = "https://www.business-standard.com/markets/research-report"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"

def scrape_business_standard():
    print("🚀 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Referer": "https://www.google.com/"
                }
            )
            page = context.new_page()

            # Apply stealth patch
            #stealth_sync(page)

            page.goto(URL, timeout=60000, wait_until="networkidle")
            print("🌐 Page requested. Waiting for table to load...")

            # Check for access denial or CAPTCHA
            if "Access Denied" in page.title() or "captcha" in page.url:
                print("🚫 Access blocked or CAPTCHA detected.")
                page.screenshot(path="access_denied.png", full_page=True)
                with open("access_denied.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                browser.close()
                return

            try:
                page.wait_for_selector("section.section-flex", timeout=3000)
                page.wait_for_selector("div.flex-70", timeout=3000)
                page.wait_for_selector("div.section-div corporate-box gl-table no-pad resrchtbl", timeout=3000)
                page.wait_for_selector("div.tbl-pd", timeout=3000)
                page.wait_for_selector("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr", timeout=90000)
            except:
                print("⚠️ Table selector not found. Saving debug info...")
                page.screenshot(path="debug_screenshot.png", full_page=True)
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                browser.close()
                return

            trs = page.query_selector_all("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr")
            if not trs:
                print("⚠️ No table rows found. Saving screenshot...")
                page.screenshot(path="final_debug.png")
                browser.close()
                return

            headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
            rows = []

            for tr in trs[:500]:
                tds = tr.query_selector_all("td")
                if len(tds) >= 5:
                    rows.append([td.inner_text().strip() for td in tds[:5]])

            if rows:
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", ts])
                print(f"✅ Successfully updated {len(rows)} rows.")
            else:
                print("⚠️ Table found but no rows extracted.")

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

scrape_business_standard()
print("business")
'''

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import google_sheets

# --- CONFIG ---
SCRAPERAPI_KEY = "97dfa0dfcf1d3829f1bd660501441c36"
URL = "https://www.business-standard.com/markets/research-report"
PROXY_URL = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={URL}"

SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"

def scrape_with_scraperapi_requests():
    print("🚀 Starting scraping with requests + ScraperAPI...")

    try:
        response = requests.get(PROXY_URL, timeout=60)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.select_one("table.cmpnydatatable_cmpnydatatable__Cnf6M")
        if not table:
            print("⚠️ Research report table not found.")
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            return

        headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
        rows = []

        for tr in table.select("tbody tr"):
            tds = tr.find_all("td")
            if len(tds) >= 5:
                row = [td.get_text(strip=True) for td in tds[:5]]
                rows.append(row)

        if rows:
            google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", ts])
            print(f"✅ Uploaded {len(rows)} rows to Google Sheet.")
        else:
            print("⚠️ Table found but no rows extracted.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

scrape_with_scraperapi_requests()

