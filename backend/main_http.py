#!/usr/bin/env python3
"""
Minimal HTTP server for One Piece chatbot
No external dependencies except FastAPI-compatible approach
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import google.generativeai as genai
from prompts import ONEPIECE_SYSTEM_PROMPT
import sys
import io

# Ensure stdout/stderr use UTF-8 on Windows consoles to avoid 'charmap' codec errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Global model
print("Initializing model...")
model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=ONEPIECE_SYSTEM_PROMPT)
print("Model initialized!")

# In-memory chat history for demo
chat_sessions = {}

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "One Piece Chatbot API"}).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Read body
        content_length = int(self.headers['Content-Length'] or 0)
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            message = data.get('message', '')
            history = data.get('history', [])
            
            print(f"[REQUEST] Message: {message[:50]}...")
            
            # Build history for Gemini
            gemini_history = []
            for msg in history:
                gemini_history.append({
                    "role": msg['role'],
                    "parts": [msg['content']]
                })
            
            print(f"  History length: {len(gemini_history)}")
            
            # Start chat
            chat_session = model.start_chat(history=gemini_history)
            
            # Send message
            print(f"  Calling Gemini API...")
            response = chat_session.send_message(message)
            
            bot_response = response.text
            print(f"  Got response ({len(bot_response)} chars)")
            
            # Update history
            updated_history = history + [
                {"role": "user", "content": message},
                {"role": "model", "content": bot_response}
            ]
            
            # Send response
            response_data = {
                "response": bot_response,
                "history": updated_history
            }
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), ChatHandler)
    print("Server running on http://0.0.0.0:8000")
    print("Press Ctrl+C to stop")
    server.serve_forever()
