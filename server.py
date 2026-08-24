from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SYSTEM_PROMPT = """You are a professional assistant for [Your Business Name].

Here is what you know about the business:
- Hours: Monday–Friday, 9am–6pm. Closed weekends.
- Services: Consultation ($50), Full service ($150), Premium package ($300).
- Location: 123 Main Street, Lagos.
- Return policy: Refunds within 14 days with receipt.
- Contact: support@yourbusiness.com or 0800-000-0000.

Only answer questions using the information above. If asked something you don't know, say:
"I don't have that information, but I can connect you with someone who does."

Speak professionally, warmly, and concisely at all times."""

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.message}
        ]
    )
    return {"reply": response.choices[0].message.content}