# AI Coding Mentor Agent

A production-grade, personalized AI agent that acts as a Socratic coding mentor. Powered by **Gemini 1.5 Pro**, **FastAPI**, and the **Model Context Protocol (MCP)**.

## 🚀 Mission
Unlike standard AI assistants that simply give you the code, the **AI Coding Mentor** is designed to help you *grow* as an engineer. It analyzes your local codebase safely, remembers your past struggles, and uses the Socratic method to lead you to the root cause of your bugs.

---

## 🏗️ Architecture

The system follows **Clean Architecture** principles, ensuring that business logic is decoupled from external services and frameworks.

### Core Components
- **FastAPI Backend:** A hardened, asynchronous API with request tracing, correlation IDs, and global error handling.
- **Gemini Service:** A resilient LLM integration layer featuring exponential backoff retries, safety guardrail handling, and stable model versioning.
- **Persistent Memory Layer:** An async SQLAlchemy system using SQLite (local) that tracks coding weaknesses, solved problems, and semantic context fragments.
- **MCP Filesystem Layer:** A secure "Sandboxed I/O" utility that allows the agent to read and list local project files while strictly preventing directory traversal attacks.
- **Observability System:** Native Google Cloud Logging integration with structured JSON logs and automatic secret redaction.

---

## 🛠️ Tech Stack
- **Language:** Python 3.12
- **Framework:** FastAPI
- **AI:** Google Gemini 1.5 Pro + Google ADK
- **Protocols:** Model Context Protocol (MCP)
- **Database:** SQLAlchemy 2.0 + SQLite (aiosqlite)
- **Deployment:** Docker + Google Cloud Run
- **Testing:** Pytest + Pytest-Asyncio

---

## 💻 Local Development

### 1. Prerequisites
- Python 3.12+
- Google Cloud Project with Gemini API enabled
- [Gemini API Key](https://aistudio.google.com/app/apikey)

### 2. Setup
```bash
# Clone and enter the repository
cd ai-coding-mentor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
APP_NAME="AI Coding Mentor"
ENVIRONMENT="development"
GEMINI_API_KEY="your_api_key_here"
DATABASE_URL="sqlite+aiosqlite:///./mentor_agent.db"
GCP_PROJECT_ID="your-project-id"
```

### 4. Run the Server
```bash
# Start FastAPI with hot reload
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for the interactive Swagger documentation.

---

## 🐳 Docker Usage

To run the full stack locally using Docker:
```bash
# Build and start services
docker-compose up --build
```
The container is hardened with a **non-root user** and uses a multi-stage build to minimize the image size.

---

## ☁️ Cloud Run Deployment

Deployment is automated via the `deploy.sh` script. It handles Artifact Registry creation, IAM service account binding, and Secret Manager integration.

```bash
# 1. Add your key to Secret Manager
# (Secret Name: GEMINI_API_KEY)

# 2. Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

---

## 🧠 Core Systems

### Model Context Protocol (MCP)
The agent uses a custom MCP implementation to gain "eyes" on your codebase. It can:
1. `list_files`: Understand your project structure.
2. `read_source_code`: Read specific files to diagnose logic errors.
**Security:** Every file operation is resolved against a mandatory `WORKSPACE_ROOT` to prevent unauthorized access.

### Persistent Memory
The agent maintains a long-term "Student Profile" for every user:
- **Weaknesses:** Tracks topics you struggle with (e.g., "Recursion," "AsyncIO") to provide targeted lessons.
- **Memories:** Semantic snippets of past interactions to ensure it doesn't repeat itself.
- **Scoring:** Memory fragments use a utility score that evolves based on relevance and recency.

---

## 🔒 Security & Safety
- **Non-Root Runtime:** The Docker container runs as a restricted user with no shell access.
- **Redaction:** The logging system automatically redacts API keys and DB strings from all JSON logs.
- **Traceability:** Every request is assigned a unique `X-Request-ID` returned in the headers and embedded in all logs.
- **Input Hardening:** Pydantic schemas enforce strict character limits and content validation to prevent DoS attacks.

---

## ❓ Troubleshooting
- **API 429 Errors:** The service uses exponential backoff. Wait a few seconds for the quota to reset.
- **SQLite Database Locked:** Ensure you are using the `aiosqlite` driver in your `DATABASE_URL`.
- **Permission Denied:** Check if your GCP Service Account has the `roles/secretmanager.secretAccessor` role.

---

## 🤝 Contributing
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. **Always** add tests for new logic in the `tests/` directory.
4. Run `pytest` to ensure 100% passing rate.
5. Commit and open a Pull Request.
