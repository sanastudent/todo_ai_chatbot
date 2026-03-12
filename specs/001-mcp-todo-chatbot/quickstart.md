# Quickstart Guide: MCP Todo Chatbot

**Feature**: 001-mcp-todo-chatbot
**Audience**: Developers setting up local development environment
**Time**: ~15 minutes

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed (`python --version`)
- **PostgreSQL** (local or Neon account)
- **OpenAI API Key** (from https://platform.openai.com/api-keys)
- **Git** for version control
- **Code editor** (VS Code recommended)

---

## 1. Clone Repository

```bash
git clone <repository-url>
cd todo-ai-chatbot
git checkout 001-mcp-todo-chatbot
```

---

## 2. Database Setup

### Option A: Neon PostgreSQL (Recommended for Production)

1. Sign up at https://neon.tech
2. Create new project: "todo-chatbot-dev"
3. Copy connection string (format: `postgresql://user:password@host/dbname`)
4. Save connection string for Step 3

### Option B: Local PostgreSQL (For Development)

```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql@15
# Ubuntu: sudo apt install postgresql-15
# Windows: Download from postgresql.org

# Start PostgreSQL service
# macOS: brew services start postgresql@15
# Ubuntu: sudo systemctl start postgresql
# Windows: Start from Services panel

# Create database
createdb todo_chatbot_dev

# Your connection string will be:
# postgresql://localhost/todo_chatbot_dev
```

---

## 3. Environment Configuration

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname  # From Step 2

# OpenAI
OPENAI_API_KEY=sk-proj-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini  # Cost-efficient model

# Better Auth (Optional for Phase 1, Required for Phase 5)
BETTER_AUTH_SECRET=your-secret-key  # Generate with: openssl rand -base64 32
BETTER_AUTH_URL=http://localhost:8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173  # Frontend URLs

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Security Note**: Never commit `.env` to version control. It's already in `.gitignore`.

---

## 4. Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

---

## 5. Install Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Expected packages:
# - fastapi>=0.100.0
# - uvicorn[standard]>=0.23.0
# - sqlmodel>=0.0.14
# - asyncpg>=0.29.0
# - python-dotenv>=1.0.0
# - openai>=1.10.0
# - mcp (Model Context Protocol SDK)
# - pydantic>=2.0.0
# - pytest>=7.4.0
# - pytest-asyncio>=0.21.0
# - httpx>=0.24.0 (for testing)
```

---

## 6. Database Migrations

```bash
# Initialize Alembic (first time only)
cd backend
alembic init migrations

# Generate initial migration
alembic revision --autogenerate -m "Initial schema: Task, Conversation, Message"

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Expected output:
#  Schema |    Name       | Type  | Owner
# --------+---------------+-------+-------
#  public | task          | table | user
#  public | conversation  | table | user
#  public | message       | table | user
```

---

## 7. Run Tests

```bash
# Unit tests (mocked database)
pytest tests/unit -v

# Integration tests (requires test database)
pytest tests/integration -v

# All tests with coverage
pytest --cov=src --cov-report=html
```

**Expected Output**:
```
tests/unit/test_mcp_tools.py::test_add_task PASSED
tests/unit/test_mcp_tools.py::test_list_tasks PASSED
tests/integration/test_api.py::test_chat_endpoint PASSED
================================ 15 passed in 2.34s ================================
```

---

## 8. Start Development Server

```bash
# From backend directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Verify Server**:
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2026-01-03T10:30:00Z"}
```

---

## 9. Test Chat Endpoint

### Using curl:

```bash
# Start new conversation
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy groceries"}'

# Expected response:
# {
#   "response": "I've added 'buy groceries' to your tasks.",
#   "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
#   "message_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
# }

# Continue conversation (use conversation_id from previous response)
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my pending tasks",
    "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  }'

# Expected response:
# {
#   "response": "You have 1 pending task:\n1. Buy groceries",
#   "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
#   "message_id": "8ea93b28-9c1f-48a2-a3b7-5d8e7f4c9d2a"
# }
```

### Using Python requests:

```python
import requests

# Start conversation
response = requests.post(
    "http://localhost:8000/api/test-user-123/chat",
    json={"message": "Add task to buy groceries"}
)
data = response.json()
print(data["response"])  # "I've added 'buy groceries' to your tasks."

conversation_id = data["conversation_id"]

# Continue conversation
response = requests.post(
    "http://localhost:8000/api/test-user-123/chat",
    json={
        "message": "Show my pending tasks",
        "conversation_id": conversation_id
    }
)
print(response.json()["response"])  # "You have 1 pending task: ..."
```

---

## 10. Frontend Setup (Optional for Backend Development)

```bash
# Install frontend dependencies
cd ../frontend
npm install

# Configure ChatKit
# Edit chatkit-config.json:
{
  "apiUrl": "http://localhost:8000/api/{userId}/chat",
  "allowedDomains": ["localhost:8000"],
  "theme": "light"
}

# Start frontend dev server
npm run dev

# Access at http://localhost:5173
```

---

## Project Structure

```
todo-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models/
│   │   │   ├── task.py          # Task SQLModel
│   │   │   ├── conversation.py  # Conversation SQLModel
│   │   │   └── message.py       # Message SQLModel
│   │   ├── mcp/
│   │   │   ├── server.py        # MCP server setup
│   │   │   └── tools.py         # MCP tool implementations
│   │   ├── api/
│   │   │   ├── routes.py        # FastAPI routes
│   │   │   └── deps.py          # Dependencies (auth, db session)
│   │   └── services/
│   │       ├── agent.py         # OpenAI Agents SDK integration
│   │       └── database.py      # Database connection/session
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_mcp_tools.py
│   │   └── integration/
│   │       └── test_api.py
│   ├── migrations/              # Alembic migrations
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   └── App.jsx              # ChatKit integration
│   ├── chatkit-config.json
│   └── package.json
├── specs/
│   └── 001-mcp-todo-chatbot/
│       ├── spec.md
│       ├── plan.md
│       ├── data-model.md
│       ├── quickstart.md (this file)
│       └── contracts/
└── .specify/
    └── memory/
        └── constitution.md
```

---

## Common Development Tasks

### Add New Dependency

```bash
# Install package
pip install package-name

# Update requirements.txt
pip freeze > backend/requirements.txt
```

### Create Database Migration

```bash
# After modifying SQLModel models
alembic revision --autogenerate -m "Add new field to Task"
alembic upgrade head
```

### Reset Database (Development Only)

```bash
# WARNING: Destroys all data
alembic downgrade base
alembic upgrade head
```

### View Logs

```bash
# Application logs (stdout)
tail -f logs/app.log

# Database queries (if echo=True in engine)
# See query logs in terminal output
```

### Debug with Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use VS Code debugger (launch.json included)
```

---

## Troubleshooting

### Database Connection Errors

**Error**: `asyncpg.exceptions.InvalidCatalogNameError: database "todo_chatbot_dev" does not exist`

**Fix**:
```bash
createdb todo_chatbot_dev
```

### OpenAI API Errors

**Error**: `openai.error.AuthenticationError: Incorrect API key provided`

**Fix**: Verify `OPENAI_API_KEY` in `.env` is correct and starts with `sk-proj-`

### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Fix**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```

---

## Next Steps

1. Read `specs/001-mcp-todo-chatbot/plan.md` for architecture details
2. Review `specs/001-mcp-todo-chatbot/contracts/` for API/MCP tool specs
3. Start implementing MCP tools (see `/sp.tasks` output when ready)
4. Write tests first (TDD approach)
5. Integrate OpenAI Agents SDK with MCP tools

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **OpenAI Agents**: https://platform.openai.com/docs/guides/agents
- **MCP Protocol**: https://modelcontextprotocol.io
- **Better Auth**: https://better-auth.com/docs/integrations/fastapi
- **Neon PostgreSQL**: https://neon.tech/docs

---

**Questions?** Open an issue or reach out to the team.
