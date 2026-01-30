import os
from dotenv import load_dotenv
import google.generativeai as genai
from prompts import ONEPIECE_SYSTEM_PROMPT

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key: {GEMINI_API_KEY[:20]}...")

genai.configure(api_key=GEMINI_API_KEY)

print("Initializing model...")
model = genai.GenerativeModel('gemini-1.5-flash')
print("Model initialized!")

print("Starting chat...")
chat = model.start_chat(history=[])
print("Chat started!")

print(f"System prompt length: {len(ONEPIECE_SYSTEM_PROMPT)} chars")
print("Sending message...")

full_message = f"{ONEPIECE_SYSTEM_PROMPT}\n\nTest"
try:
    response = chat.send_message(full_message)
    print("Response received!")
    print("First 200 chars:", response.text[:200])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
