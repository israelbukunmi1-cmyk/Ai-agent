import gspread
from google.oauth2.service_account import Credentials
import os
import json

def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    
    client = gspread.authorize(creds)
    sheet = client.open("israel sheet").sheet1  # must match your actual Sheet name
    return sheet

def log_conversation(user_message, ai_reply):
    sheet = get_sheet()
    sheet.append_row([user_message, ai_reply])