import sys
import json
import os
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

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print(json.dumps({"error": "GEMINI_API_KEY not configured"}))
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def main():
    try:
        data = json.load(sys.stdin)
        message = data.get('message', '')
        history = data.get('history', [])

        gemini_history = []
        for m in history:
            gemini_history.append({
                "role": m.get('role', 'user'),
                "parts": [m.get('content', '')]
            })

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=ONEPIECE_SYSTEM_PROMPT)
        chat = model.start_chat(history=gemini_history)
        resp = chat.send_message(message)

        output = {"response": resp.text}
        json.dump(output, sys.stdout, ensure_ascii=False)
    except Exception as e:
        json.dump({"error": str(e)}, sys.stdout)

if __name__ == '__main__':
    main()
