from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
import json

from knowledge_base import SYSTEM_PROMPT
from email_helper import send_email
from sheets_helper import log_order
from calendar_helper import book_appointment

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Log a customer's order once they provide their details and what they want to buy",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer's name"},
                    "phone_number": {"type": "string", "description": "Customer's phone number"},
                    "address": {"type": "string", "description": "Delivery address"},
                    "product_ordered": {"type": "string", "description": "The product(s) the customer wants to order"},
                    "quantity": {"type": "string", "description": "Quantity of the product ordered"},
                    "email": {"type": "string", "description": "Customer's email address, if provided"}
                },
                "required": ["name", "phone_number", "address", "product_ordered", "quantity"]
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

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools
    )

    ai_message = response.choices[0].message

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

        elif tool_call.function.name == "place_order":
            log_order(
                name=args["name"],
                phone_number=args["phone_number"],
                address=args["address"],
                product_ordered=args["product_ordered"],
                quantity=args["quantity"],
                email=args.get("email", "")
            )
            final_reply = f"Thanks {args['name']}! Your order for {args['quantity']} x {args['product_ordered']} has been received. We'll contact you at {args['phone_number']} to confirm delivery."

        else:
            final_reply = "Sorry, I couldn't complete that action."
    else:
        final_reply = ai_message.content

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