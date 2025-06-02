import os
import json
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]



def get_google_credentials():
    creds = ServiceAccountCredentials.from_json_keyfile_name("pags-429207-03ef3b521109.json", scope)
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

        # Get number of columns from the sheet
        

        worksheet.append_row(footer_row)
        print("🕒 Timestamp footer appended.")
    except Exception as e:
        print(f"❌ Footer append error: {e}")

