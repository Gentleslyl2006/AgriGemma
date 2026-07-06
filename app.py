"""
AgriGemma backend
------------------
Runs entirely on the local machine / local network. No cloud API calls,
no internet dependency at inference time — the whole point of the app.

Talks to Gemma 4 via a local Ollama instance (https://ollama.com), which is
the standard way to run Gemma models offline on a laptop or small device.

Setup (one-time, needs internet to download the model):
    1. Install Ollama: https://ollama.com/download
    2. Pull the model:  ollama pull gemma4:e4b   (swap for the size that fits your hardware)
    3. Run this server: uvicorn app:app --host 0.0.0.0 --port 8000

After setup, everything below runs with zero internet access.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="AgriGemma Backend")

# Allow the local frontend (served from file:// or a local dev server) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:e4b"  # swap for a smaller tag if this is too slow on your hardware

SYSTEM_PROMPT = """You are AgriGemma, an offline AI assistant for Nigerian smallholder farmers.

Your users have limited literacy, limited internet, and speak English or
Nigerian Pidgin. They ask about crops (cassava, maize, yam, rice, tomato,
pepper) and livestock (poultry, goats, cattle).

Rules:
1. Answer in short, simple sentences (max 3-4 sentences per response).
2. Avoid technical jargon. Use words a farmer without formal agri-training
   would know.
3. If the user writes in Pidgin, reply in Pidgin. If English, reply in
   English.
4. Always give a practical, actionable next step.
5. If the problem sounds serious (disease outbreak, chemical poisoning,
   large-scale crop failure, an animal that may die soon), start your reply
   with the exact tag [FLAG] followed by a one-sentence reason, then your
   advice on the next line.
6. Never invent facts about specific pesticide/drug dosages you're unsure
   of — give general safe guidance instead and recommend checking the
   product label or an extension officer.
7. Assume no internet access — don't reference looking things up online.
"""


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str
    needs_expert: bool
    flag_reason: str | None = None


@app.post("/ask", response_model=Answer)
def ask(payload: Question):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": payload.question},
            ],
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    raw_reply = response.json()["message"]["content"].strip()

    needs_expert = False
    flag_reason = None

    if raw_reply.startswith("[FLAG]"):
        needs_expert = True
        remainder = raw_reply[len("[FLAG]"):].strip()
        # First line is the flag reason, rest is the advice
        parts = remainder.split("\n", 1)
        flag_reason = parts[0].strip()
        raw_reply = parts[1].strip() if len(parts) > 1 else parts[0].strip()

    return Answer(answer=raw_reply, needs_expert=needs_expert, flag_reason=flag_reason)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}
