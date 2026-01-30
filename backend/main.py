"""
Simple sync FastAPI backend for One Piece Chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional
import asyncio
import sys
import io

# Ensure stdout/stderr use UTF-8 on Windows consoles to avoid 'charmap' codec errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import subprocess
import sys
import json
from prompts import ONEPIECE_SYSTEM_PROMPT

# Load env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not configured")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

print("=" * 50)
print("Initializing GenerativeModel...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=ONEPIECE_SYSTEM_PROMPT)
    print("[OK] Model initialized successfully!")
except Exception as e:
    print(f"[ERROR] {e}")
    raise

print("=" * 50)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = None

class ChatResponse(BaseModel):
    response: str
    history: List[Message]

@app.get("/")
def root():
    return {"message": "One Piece Chatbot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"\n[API /chat] Received: {request.message[:50]}...")

    try:
        # Ensure history is not None
        history = request.history if request.history else []
        print(f"  History length: {len(history)}")

        # Build Gemini history
        gemini_history = []
        for msg in history:
            gemini_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })

        print(f"  Starting chat session (threaded)...")

        # Call Gemini via an isolated subprocess worker to avoid crashing the uvicorn process
        def _call_gemini_subproc(message, history_payload):
            payload = {"message": message, "history": history_payload}
            try:
                proc = subprocess.run(
                    [sys.executable, "gemini_worker.py"],
                    input=json.dumps(payload, ensure_ascii=False),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            except Exception as e:
                raise

            if proc.returncode != 0:
                # Try to parse stdout for error message
                try:
                    data = json.loads(proc.stdout)
                    raise RuntimeError(data.get('error', proc.stderr.strip()))
                except Exception:
                    raise RuntimeError(proc.stderr.strip() or 'Unknown subprocess error')

            try:
                data = json.loads(proc.stdout)
                if 'error' in data:
                    raise RuntimeError(data['error'])
                return data.get('response', '')
            except json.JSONDecodeError:
                # If output is not JSON, return raw stdout
                return proc.stdout

        bot_response = await asyncio.to_thread(_call_gemini_subproc, request.message, gemini_history)

        # Build response history
        updated_history = history + [
            Message(role="user", content=request.message),
            Message(role="model", content=bot_response)
        ]

        print(f"  Returning response ({len(bot_response)} chars)")
        return ChatResponse(response=bot_response, history=updated_history)

    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset_conversation():
    return {"message": "Conversation reset", "history": []}

if __name__ == "__main__":
    import uvicorn
    print("\nStarting uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")