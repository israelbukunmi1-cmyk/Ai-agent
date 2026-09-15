import requests
import os

def send_email(subject, body, to_email):
    api_key = os.environ.get("RESEND_API_KEY")

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "from": "onboarding@resend.dev",
            "to": [to_email],
            "subject": subject,
            "text": body
        }
    )
    print("Email send response:", response.status_code, response.text)