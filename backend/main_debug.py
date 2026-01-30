from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional
from prompts import ONEPIECE_SYSTEM_PROMPT

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("=" * 50)
print("BACKEND STARTUP")
print("=" * 50)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str
    history: List[Message]

# Initialize model
print("Initializing GenerativeModel...")
model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=ONEPIECE_SYSTEM_PROMPT)
print("Model initialized!")

@app.get("/")
async def root():
    return {"message": "One Piece Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    print(f"\n[REQUEST] Message: {request.message[:50]}...")
    try:
        print("  [1] Building history...")
        gemini_history = []
        for msg in request.history:
            gemini_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        print(f"  [2] Starting chat (history length: {len(gemini_history)})...")
        chat_session = model.start_chat(history=gemini_history)
        
        print(f"  [3] Sending message to Gemini...")
        response = chat_session.send_message(request.message)
        
        print(f"  [4] Got response ({len(response.text)} chars)")
        bot_response = response.text
        
        print(f"  [5] Building response...")
        updated_history = request.history + [
            Message(role="user", content=request.message),
            Message(role="model", content=bot_response)
        ]
        
        print(f"  [✓] Returning response")
        return ChatResponse(
            response=bot_response,
            history=updated_history
        )
        
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
