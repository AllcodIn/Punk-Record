#!/usr/bin/env python3
"""
Minimal test server to debug the issue
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from prompts import ONEPIECE_SYSTEM_PROMPT
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("Initializing model...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=ONEPIECE_SYSTEM_PROMPT)
    print("Model initialized successfully!")
except Exception as e:
    print(f"ERROR initializing model: {type(e).__name__}: {e}")
    exit(1)

# Test the chat
print("\nStarting chat session...")
try:
    chat = model.start_chat(history=[])
    print("Chat session started!")
except Exception as e:
    print(f"ERROR starting chat: {type(e).__name__}: {e}")
    exit(1)

print("\nSending first message...")
try:
    response = chat.send_message("Bonjour! Qui es-tu?")
    print("SUCCESS! Response received.")
    print(f"Response (first 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"ERROR sending message: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nSending second message...")
try:
    response = chat.send_message("Dis-moi plus sur Luffy")
    print("SUCCESS! Second response received.")
    print(f"Response (first 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"ERROR sending second message: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ All tests passed!")
