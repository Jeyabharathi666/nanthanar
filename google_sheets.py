import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Updated scope list for Google Sheets & Drive API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_credentials():
    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON_")
    if not raw_json:
        raise EnvironmentError("Missing environment variable: GOOGLE_SERVICE_ACCOUNT_JSON_")
    json_dict = json.loads(raw_json)
    creds = Credentials.from_service_account_info(json_dict, scopes=SCOPES)
    return creds

def authorize_google_sheets(credentials):
    return gspread.authorize(credentials)

def update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows):
    try:
        credentials = get_google_credentials()
        gc = authorize_google_sheets(credentials)
        sh = gc.open_by_key(sheet_id)

        try:
            worksheet = sh.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=worksheet_name, rows="100", cols="20")

        worksheet.clear()
        worksheet.append_row(headers)
        worksheet.append_rows(rows)
        print(f"✅ Data updated in worksheet: {worksheet_name}")

    except Exception as e:
        print(f"❌ Google Sheet update error: {e}")

def append_footer(sheet_id, worksheet_name, footer_row):
    try:
        credentials = get_google_credentials()
        gc = authorize_google_sheets(credentials)
        worksheet = gc.open_by_key(sheet_id).worksheet(worksheet_name)
        worksheet.append_row(footer_row)
        print("🕒 Timestamp footer appended.")
    except Exception as e:
        print(f"❌ Footer append error: {e}")
