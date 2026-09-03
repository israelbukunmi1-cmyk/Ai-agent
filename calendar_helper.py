from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

def get_calendar_service():
    scopes = ["https://www.googleapis.com/auth/calendar"]
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    service = build("calendar", "v3", credentials=creds)
    return service

def book_appointment(date, time, customer_name):
    service = get_calendar_service()

    start_datetime = f"{date}T{time}:00"
    hour, minute = map(int, time.split(":"))
    end_hour = hour if minute < 30 else hour + 1
    end_minute = minute + 30 if minute < 30 else minute - 30
    end_datetime = f"{date}T{end_hour:02d}:{end_minute:02d}:00"

    event = {
        "summary": f"Appointment with {customer_name}",
        "start": {"dateTime": start_datetime, "timeZone": "Africa/Lagos"},
        "end": {"dateTime": end_datetime, "timeZone": "Africa/Lagos"},
    }

    created_event = service.events().insert(calendarId="israelbukunmi1@gmail.com", body=event).execute()
    return created_event.get("htmlLink")