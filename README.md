# AI Coding Mentor - Fullstack Project

A production-grade, personalized AI agent that acts as a Socratic coding mentor.

## Structure
- `/backend`: Hardened FastAPI + Gemini + Persistent Memory (SQLAlchemy/SQLite).
- `/frontend`: Premium React UI + Structured Rendering + Syntax Highlighting.

## Quick Start (Local)

### 1. Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```powershell
cd frontend
npm install
npm run dev
```

The application will be available at http://localhost:3000
