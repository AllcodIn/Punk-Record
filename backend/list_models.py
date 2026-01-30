import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("Available models:")
for model in genai.list_models():
    print(f"  - {model.name}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"    Methods: {model.supported_generation_methods}")
