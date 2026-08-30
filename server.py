from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
import json

from knowledge_base import SYSTEM_PROMPT
from email_helper import send_email
from sheets_helper import log_conversation
from calendar_helper import book_appointment

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define the tools (functions) the AI is allowed to call
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment on the calendar when a customer requests one",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in 24-hour HH:MM format"},
                    "customer_name": {"type": "string", "description": "The customer's name"}
                },
                "required": ["date", "time", "customer_name"]
            }
        }
    }
]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request.message}
    ]

    # Step 1: Ask the AI - it might reply normally, or ask to call a tool
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools
    )

    ai_message = response.choices[0].message

    # Step 2: Check if the AI wants to call a tool
    if ai_message.tool_calls:
        tool_call = ai_message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "book_appointment":
            calendar_link = book_appointment(
                date=args["date"],
                time=args["time"],
                customer_name=args["customer_name"]
            )
            final_reply = f"You're booked, {args['customer_name']}! Here's your event: {calendar_link}"
        else:
            final_reply = "Sorry, I couldn't complete that action."
    else:
        final_reply = ai_message.content

    # Step 3: Log the conversation to Sheets
    try:
        log_conversation(request.message, final_reply)
    except Exception as e:
        print(f"Sheets logging failed: {e}")

    # Step 4: Email yourself if the AI couldn't answer something
    if "I don't have that information" in final_reply:
        try:
            send_email(
                subject="Unanswered customer question",
                body=f"Customer asked: {request.message}",
                to_email=os.environ.get("NOTIFY_EMAIL")
            )
        except Exception as e:
            print(f"Email failed: {e}")

    return {"reply": final_reply}