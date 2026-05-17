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
# Copy .env.example to .env and add your Gemini API Key
uvicorn app.main:app --reload --port 8080
```

### 2. Frontend
```powershell
cd frontend
npm install
# Ensure .env exists with VITE_API_BASE_URL=http://localhost:8080
npm run dev
```

## Production Deployment

### Backend (Google Cloud Run)
The backend is deployed to: `https://ai-mentor-backend-309500508226.us-central1.run.app`

### Frontend Configuration
When deploying the frontend (e.g., to Vercel), ensure `VITE_API_BASE_URL` is set to the production backend URL.
