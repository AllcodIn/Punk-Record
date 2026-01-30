# One Piece Chatbot

A local One Piece fan/expert chatbot (frontend + Python backend) that uses Google Generative AI (Gemini) for question answering, chapter analysis and fan theories. Designed for local development on Windows with a stable minimal HTTP fallback.

**Features**
- **Local frontend:** Single-file web UI at [frontend/index.html](frontend/index.html)
- **Python backend:** FastAPI entrypoint (`backend/main.py`) and a minimal stable HTTP server (`backend/main_http.py`) for Windows
- **Isolated worker:** `backend/gemini_worker.py` runs Gemini calls in a subprocess to avoid crashing the main server
- **Detailed system prompt:** `backend/prompts.py` contains the One Piece expert system prompt and spoiler rules

**Tech stack**
- Python 3.12
- google-generativeai (Gemini SDK)
- FastAPI / uvicorn (optional)
- Vanilla HTML/CSS/JS frontend

## Requirements
- A Google Generative API key stored in `backend/.env` as `GEMINI_API_KEY`
- A Python 3.12 virtual environment

## Quickstart (Windows)
1. Open PowerShell and create a venv from the `backend` folder:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2. Create `backend/.env` with your API key:

```
GEMINI_API_KEY=sk-...
```

3. Start the stable minimal server (recommended on Windows):

```powershell
& .\.venv\Scripts\Activate.ps1
python main_http.py
```

Or run the FastAPI server (optional):

```powershell
& .\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. Open the frontend: open [frontend/index.html](frontend/index.html) in your browser. The UI calls `http://localhost:8000/chat` by default.

## API
- `GET /health` → `{ "status": "healthy" }`
- `POST /chat`
  - Request JSON: `{ "message": "...", "history": [{ "role": "user"|"model", "content": "..." }, ...] }`
  - Response JSON: `{ "response": "...", "history": [...] }`

Example PowerShell request:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/chat -Method POST -Body (@{
  message = "Who is Joy Boy?"
  history = @()
} | ConvertTo-Json -Depth 5) -ContentType 'application/json'
```

## Notes
- The long One Piece system prompt and spoiler policy live in [backend/prompts.py](backend/prompts.py).
- On some Windows setups `uvicorn` showed unstable behavior; `main_http.py` provides a robust fallback.
- The code forces UTF-8 for stdout/stderr to avoid Windows console encoding issues.

## Troubleshooting
- If you get API errors, verify `GEMINI_API_KEY` and network connectivity.
- If the server stops unexpectedly under `uvicorn`, retry with `main_http.py`.

## Contributing & License
- Add an appropriate license (e.g., MIT) and open issues/PRs for improvements.

---

If you want, I can also commit this README to Git and create a short commit message.
# PunkRecord — One Piece Chatbot

This project contains a FastAPI backend and a static frontend to chat with a One Piece expert persona.

Quick start (Windows)

1. Create and activate the venv (if not already):

```powershell
cd C:\Users\TUF-F16\Desktop\PunkRecord\backend
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the lightweight backend server (recommended for local use):

```powershell
cd C:\Users\TUF-F16\Desktop\PunkRecord\backend
& .\.venv\Scripts\Activate.ps1
python main_http.py
```

Alternatively, run the helper to start the server in a detached window:

```powershell
cd C:\Users\TUF-F16\Desktop\PunkRecord\backend
& .\.venv\Scripts\Activate.ps1
.\start_server.ps1
```

3. Open the frontend in your browser:

http://localhost:5500

Notes
- The backend uses the Google generative AI client and requires a `GEMINI_API_KEY` stored in `backend/.env`.
- If you want to use the FastAPI/uvicorn entrypoint instead, run `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8000`.
- For local stability we added `main_http.py` (lightweight fallback) and `gemini_worker.py` (isolated worker) to avoid the uvicorn-process termination observed on some Windows environments.

If anything breaks, paste the server terminal output here and I'll help triage.

