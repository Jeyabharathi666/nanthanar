'''import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "pags-429207-03ef3b521109.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_google_credentials():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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


import gspread
from google.oauth2.service_account import Credentials

# 🔐 Path to your service account JSON key
SERVICE_ACCOUNT_FILE = "path/to/your_service_account.json"

# 🔒 Scope for Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ Authorize client
def get_gspread_client():
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print("❌ Authorization error:", e)
        raise

# 📋 Update entire worksheet with headers and rows
def update_google_sheet_by_name(sheet_id, worksheet_name, headers, rows):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
        sheet.clear()
        sheet.append_row(headers)
        for row in rows:
            sheet.append_row(row)
        print("✅ Google Sheet updated successfully.")
    except Exception as e:
        print("❌ Google Sheet update error:", e)

# 🕒 Append footer (like a timestamp or summary row)
def append_footer(sheet_id, worksheet_name, footer_row):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
        sheet.append_row(footer_row)
        print("✅ Footer appended successfully.")
    except Exception as e:
        print("❌ Footer append error:", e)''''''
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load the credentials from the JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name("eng-flux-421206-009c2355c702.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open your sheet by key or name
sheet = client.open_by_key("1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg").sheet1

# Use get_all_values() to retrieve all data in the sheet
data = sheet.get_all_values()
# Optionally, append a new row
sheet.append_row(["Sanjay", "Test", 123])
# Print the data to verify
print("Sheet Data:")
for row in data:
    print(row)'''


'''

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
creds = ServiceAccountCredentials.from_json_keyfile_name(".json", scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open("1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg").sheet1

# Fetch data from an API
response = requests.get('https://api.example.com/data')
data = response.json()  # Assuming the API returns JSON data

# Prepare data for the sheet (e.g., list of rows)
rows_to_add = []

# Assuming your data is a list of dictionaries, extract values as rows
for item in data:
    rows_to_add.append([item['field1'], item['field2'], item['field3']])  # Adjust fields as per your data

# Append data to Google Sheet
for row in rows_to_add:
    sheet.append_row(row)

print("Data added to Google Sheet!")



import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("eng-flux-421206-009c2355c702.json", scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open("1TYoAk_rd43IEFgyuPrfpi5Q7nXoM3bgolEeoWO18nRg").sheet1

# Read data from CSV file using pandas
df = pd.read_csv('data.csv')  # Replace with your CSV file

# Convert DataFrame to list of lists
rows_to_add = df.values.tolist()

# Append data to Google Sheet
for row in rows_to_add:
    sheet.append_row(row)

print("Data added to Google Sheet!")'''

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]



def get_google_credentials():
    # Read from GitHub Secrets
    service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
    creds = Credentials.from_service_account_info(service_account_info)
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

