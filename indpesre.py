import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright
import time
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
SCREENER_EMAIL    = os.environ.get("EMAIL")
SCREENER_PASSWORD = os.environ.get("PASSWORD")
GOOGLE_CREDS_JSON = os.environ.get("NEW")  # JSON string
SHEET_ID = "1VtgTb36SB65HtQQpjcagh4cxr7pDGcLzGpR9ScE4vdA"
SHEET_TAB = "FULL"
DATA_START_ROW = 4

OUTPUT_HEADERS = [
    "PE", "BOKVAL", "DIVDND",
    "ROCE", "ROE", "Face",
    "INDPE", "FII", "DII", "DEBT","PLDGE",
    "Promoters"
]

def login(page):
    page.goto("https://www.screener.in/login/")
    page.fill("input[name='username']", SCREENER_EMAIL)
    page.fill("input[name='password']", SCREENER_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url("**/dash/**")
    print("✅ Logged in")

def scrape_stock(page, symbol):

    # def extract():
    #     data = {h: "" for h in OUTPUT_HEADERS}

    #     # SUMMARY
    #     for li in page.query_selector_all(".company-ratios li"):
    #         name = li.query_selector("span.name").inner_text().strip()
    #         val_el = li.query_selector("span.nowrap span.number, span.number")
    #         val = val_el.inner_text().strip() if val_el else ""

    #         if name == "Stock P/E":
    #             data["PE"] = val
    #         elif name == "Book Value":
    #             data["BOKVAL"] = val
    #         elif name == "Dividend Yield":
    #             data["DIVDND"] = val
    #         elif name == "ROCE":
    #             data["ROCE"] = val
    #         elif name == "ROE":
    #             data["ROE"] = val
    #         elif name == "Face Value":
    #             data["Face"] = val


    #     # TOP RATIOS
    #     for li in page.query_selector_all("#top-ratios li"):
    #         name = li.query_selector("span.name").inner_text().strip()
    #         val_el = li.query_selector("span.nowrap span.number, span.number")
    #         val = val_el.inner_text().strip() if val_el else ""

    #         lname = name.lower()

    #         if "industry PE" in lname:
    #             data["INDPE"] = val
            
    #         elif "fii holding" in lname:
    #             data["FII"] = val
            
    #         elif "dii holding" in lname:
    #             data["DII"] = val
    #         elif "Debt" in lname:
    #             data["DEBT"] = val
            
    #         elif "Pledged percentage" in lname:
    #             data["PLDGE"] = val        


    #     # PROMOTERS
    #     for row in page.query_selector_all("#shareholding table tr"):
    #         if "Promoter holding" in row.inner_text():
    #             cols = row.query_selector_all("td")
    #             if cols:
    #                 data["Promoters"] = cols[-1].inner_text().strip()
    #             break

    #     return data
    def extract():

        def get_text(xpath):
            try:
                return page.locator(f"xpath={xpath}").inner_text().strip()
            except:
                return ""
    
        data = {}
    
        data["PE"] = get_text(
            "//li[span[contains(text(),'Stock P/E')]]/span[2]"
        )
    
        data["BOKVAL"] = get_text(
            "//li[span[contains(text(),'Book Value')]]/span[2]"
        )
    
        data["DIVDND"] = get_text(
            "//li[span[contains(text(),'Dividend Yield')]]/span[2]"
        )
    
        data["ROCE"] = get_text(
            "//li[span[contains(text(),'ROCE')]]/span[2]"
        )
    
        data["ROE"] = get_text(
            "//li[span[contains(text(),'ROE')]]/span[2]"
        )
    
        data["Face"] = get_text(
            "//li[span[contains(text(),'Face Value')]]/span[2]"
        )
    
        data["Promoters"] = get_text(
            "//li[span[contains(text(),'Promoter holding')]]/span[2]"
        )
    
        data["PLDGE"] = get_text(
            "//li[span[contains(text(),'Pledged percentage')]]/span[2]"
        )
    
        data["DEBT"] = get_text(
            "//li[span[contains(text(),'Debt')]]/span[2]"
        )
    
        data["INDPE"] = get_text(
            "//li[span[contains(text(),'Industry PE')]]/span[2]"
        )
    
        data["FII"] = get_text(
            "//li[span[contains(text(),'FII')]]/span[2]"
        )
    
        data["DII"] = get_text(
            "//li[span[contains(text(),'DII')]]/span[2]"
        )
    
        return data
    # 🔹 TRY CONSOLIDATED
    page.goto(f"https://www.screener.in/company/{symbol}/consolidated/")
    try:
        page.wait_for_selector("#top-ratios li span.name", timeout=4000)
        page.wait_for_timeout(800)
    except:
        pass

    data = extract()

    # 🔴 SIMPLE FALLBACK
    if not data["INDPE"] or data["INDPE"] == "":
        print(f"→ fallback: {symbol}")

        page.goto(f"https://www.screener.in/company/{symbol}/")
        try:
            page.wait_for_selector("#top-ratios li span.name", timeout=4000)
            page.wait_for_timeout(800)
        except:
            pass

        data = extract()

    return data


if __name__ == "__main__":

    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    #sheet = gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(SHEET_TAB)
    gc = gspread.authorize(creds)
    
    flist_sheet = gc.open_by_key(SHEET_ID).worksheet("FLIST")
    nt_sheet = gc.open_by_key(SHEET_ID).worksheet("nt")
    # =====================================================
    # Sync NT -> FLIST
    # =====================================================
    
    # Existing symbols in FLIST
    existing_symbols = {
        row[1].strip().upper()
        for row in flist_sheet.get_all_values()[DATA_START_ROW-1:]
        if len(row) > 1 and row[1].strip()
    }
    
    # Read every row from NT
    nt_rows = nt_sheet.get_all_values()[DATA_START_ROW-1:]
    
    rows_to_append = []
    
    for row in nt_rows:
    
        if len(row) < 2:
            continue
    
       
        symbol = row[1].strip().upper()
        
       
    
        if not symbol:
            continue
    
        if symbol not in existing_symbols:
    
            # Make row length same as FLIST
            flist_data = flist_sheet.get_all_values()

            header_length = len(flist_data[0])
            while len(row) < header_length:
                row.append("")
    
            rows_to_append.append(row)
            existing_symbols.add(symbol)
    
    if rows_to_append:
        flist_sheet.append_rows(rows_to_append)
        print(f"✅ {len(rows_to_append)} new stocks added to FLIST")
    else:
        print("✅ No new stocks found")    
    symbols = [
        s.strip().upper()
        for s in flist_sheet.col_values(2)[DATA_START_ROW - 1:]
        if s.strip()
    ]

    print(f"📋 {len(symbols)} symbols found")

    flist_sheet.update(values=[OUTPUT_HEADERS], range_name="M1:X1")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        login(page)

        for i, symbol in enumerate(symbols):
            row_num = DATA_START_ROW + i
            print(f"\n[{i+1}/{len(symbols)}] {symbol}")

            try:
                data = scrape_stock(page, symbol)
            except Exception as e:
                print("ERROR:", e)
                data = {h: "" for h in OUTPUT_HEADERS}

            row_values = [data.get(h, "") for h in OUTPUT_HEADERS]

            # ✅ ROW BY ROW UPDATE
            flist_sheet.update(
                values=[row_values],
                range_name=f"M{row_num}:X{row_num}"
            )

            print(f"✅ Row {row_num} updated")
            time.sleep(0.4)
        timestamp = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%d-%m-%Y %H:%M:%S IST")

        last_row = len(symbols) + DATA_START_ROW + 2

        flist_sheet.update(
            values=[[f"Last Updated: {timestamp}"]],
            range_name=f"M{last_row}"
        )

        browser.close()


    print("\n🎉 DONE")
