# AgriGemma

Offline voice/text farming advice for Nigerian smallholder farmers, powered by Gemma 4.

Built for the Gemma 4 Hackathon Sprint — Agriculture & Food Security track.

## What it does

A farmer taps a mic button or types a question about a sick animal or struggling
crop, in English or Nigerian Pidgin. Gemma 4, running fully on-device, gives
short, practical advice — and flags when the issue is serious enough to need
a vet or extension officer.

## Architecture

```
frontend/     PWA — HTML/CSS/JS, works offline after first load
              (Web Speech API for voice in/out, no cloud STT/TTS)
backend/      FastAPI service that applies the AgriGemma system prompt
              and calls a local Gemma 4 model via Ollama
```

Only the *initial model download* needs internet. After that, the whole
loop — voice capture, inference, response — runs with zero connectivity.

## Setup

### 1. Install and run Gemma 4 locally (one-time, needs internet)

```bash
# install Ollama: https://ollama.com/download
ollama pull gemma4:e4b    # swap for a smaller tag if this is too slow on your hardware
```

### 2. Run the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Open the frontend

```bash
cd frontend
python3 -m http.server 5500
```

Visit `http://localhost:5500` in a browser (Chrome/Edge recommended for
voice support). From here on, disconnect from the internet — it still works.

## System prompt

The full system prompt that shapes Gemma's behavior (tone, language
switching, safety guardrails around dosages, and the expert-flagging logic)
lives in `backend/app.py` under `SYSTEM_PROMPT`.

## Notes for judges

- The `[FLAG]` tag convention lets Gemma signal "this needs a human expert"
  in a way the frontend can parse into a visible warning, without needing a
  second model call or classifier.
- Quick-tap topic chips are included for low-literacy users who may prefer
  not to type or speak a full sentence.
