import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime

def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    
    client = gspread.authorize(creds)
    sheet = client.open("israel sheet").sheet1  # must match your actual Sheet name
    return sheet

def log_order(name, phone_number, address, product_ordered, quantity, email="", status="New Order"):
    sheet = get_sheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        timestamp,
        name,
        phone_number,
        address,
        email,
        product_ordered,
        quantity,
        status
    ])