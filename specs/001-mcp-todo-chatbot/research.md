# Research: MCP Todo Chatbot

**Feature**: 001-mcp-todo-chatbot
**Date**: 2026-01-03
**Purpose**: Resolve technical unknowns and establish implementation patterns

## Technical Context Resolution

### Language/Version
**Decision**: Python 3.11+
**Rationale**: Mandated by constitution. Python 3.11 provides:
- Improved error messages for debugging
- Performance improvements (10-60% faster than 3.10)
- Native support for typing features needed for SQLModel
- Compatibility with FastAPI 0.100+ and SQLModel

**Alternatives Considered**: None - constitution requirement

---

### Primary Dependencies
**Decision**:
- FastAPI 0.100+
- SQLModel 0.0.14+
- OpenAI Python SDK 1.10+
- MCP SDK (Python)

**Rationale**:
- **FastAPI**: Mandated by constitution. Provides async support, automatic OpenAPI docs, dependency injection, and excellent performance
- **SQLModel**: Mandated by constitution. Combines Pydantic validation with SQLAlchemy ORM, perfect for FastAPI integration
- **OpenAI Python SDK**: Required for OpenAI Agents SDK integration
- **MCP SDK**: Required for Model Context Protocol tool implementation

**Alternatives Considered**: None for FastAPI/SQLModel (constitution). For AI layer, considered LangChain but OpenAI Agents SDK is more direct for agent-based workflows.

---

### Storage
**Decision**: Neon PostgreSQL (Serverless)
**Rationale**: Mandated by constitution. Benefits:
- Serverless scaling (auto-pause when idle, scales to zero)
- PostgreSQL compatibility (full ACID, relational integrity)
- Built-in connection pooling
- Branch databases for testing

**Connection Strategy**:
- Use `asyncpg` driver for async operations
- Connection string from environment variable
- SQLModel async engine with connection pooling

**Alternatives Considered**: None - constitution requirement

---

### Testing
**Decision**: pytest with async support
**Rationale**:
- Industry standard for Python testing
- Native async test support via `pytest-asyncio`
- Rich plugin ecosystem (coverage, fixtures, mocking)
- Integrates well with FastAPI testing utilities

**Testing Strategy**:
- **Unit tests**: MCP tools in isolation (mocked database)
- **Integration tests**: API endpoint with test database
- **Contract tests**: Validate MCP tool signatures match spec

**Tools**:
- `pytest` - test framework
- `pytest-asyncio` - async test support
- `httpx` - FastAPI test client
- `pytest-cov` - coverage reporting

**Alternatives Considered**: unittest (too verbose), nose (deprecated)

---

### Target Platform
**Decision**: Linux server (containerized)
**Rationale**:
- Backend API service (no GUI)
- Deployment via Docker container
- Cloud-agnostic (can run on AWS, GCP, Azure, Railway, Render)
- Development on Windows/Mac/Linux via Docker

**Deployment Strategy**:
- Dockerfile with Python 3.11 slim base
- Environment variables for config (DATABASE_URL, OPENAI_API_KEY)
- Health check endpoint for orchestration
- CORS configured for ChatKit frontend domain

**Alternatives Considered**: Serverless functions (too stateful for conversation management), native deployment (less portable)

---

### Project Type
**Decision**: Web application (backend API + frontend client)
**Rationale**:
- Backend: Python FastAPI server exposing REST API
- Frontend: OpenAI ChatKit (pre-built React chat UI)
- Separation allows independent deployment and scaling

**Structure**:
```
backend/
├── src/
│   ├── models/         # SQLModel database models
│   ├── mcp/            # MCP tool implementations
│   ├── api/            # FastAPI routes
│   └── services/       # Business logic
└── tests/

frontend/
├── chatkit-config.json # ChatKit configuration
└── index.html          # Entry point
```

**Alternatives Considered**: Monorepo with Next.js (overkill for ChatKit usage), single Python app serving static files (less clear separation)

---

### Performance Goals
**Decision**:
- API response time: < 2s (95th percentile)
- Database query time: < 100ms (95th percentile)
- Concurrent users: 100+ without degradation > 20%
- Message throughput: 10 messages/second/user

**Rationale**:
- Chat UX requires sub-2s responses for natural feel
- Database queries are simple (indexed lookups) so < 100ms is achievable
- Hackathon scale is ~100 users max
- Users rarely send > 10 messages/second

**Monitoring**:
- FastAPI middleware for request timing
- Database query logging
- OpenAI API latency tracking

**Alternatives Considered**: Higher throughput (not needed for hackathon scale)

---

### Constraints
**Decision**:
- **Latency**: API p95 < 2s (constitution requirement)
- **Security**: User ID validation on every request, no cross-user data access (constitution requirement)
- **Stateless**: All conversation state in database, no server-side sessions
- **Cost**: Use OpenAI GPT-4o-mini for cost efficiency (vs GPT-4)

**Rationale**:
- Latency: Chatbot UX requires fast responses
- Security: Multi-tenant app requires strict data isolation
- Stateless: Allows horizontal scaling and server restarts without losing state
- Cost: Mini model is 10x cheaper and sufficient for task management domain

**Implementation**:
- Middleware validates user_id exists and matches authenticated user
- All queries filtered by user_id
- Database indexes on user_id for fast lookups
- Use GPT-4o-mini unless user explicitly needs GPT-4 reasoning

**Alternatives Considered**: Session-based state (doesn't scale), permissive auth (security risk)

---

### Scale/Scope
**Decision**:
- **Users**: 10-100 concurrent users (hackathon scale)
- **Tasks per user**: Up to 1,000 tasks
- **Conversations per user**: Up to 50 conversations
- **Messages per conversation**: Up to 500 messages
- **Database size**: < 10 GB

**Rationale**:
- Hackathon Phase 3 is proof-of-concept, not production
- Limits prevent abuse and runaway costs
- Database indexes ensure performance at this scale

**Scaling Strategy** (if needed post-hackathon):
- Horizontal API scaling (stateless design)
- Database read replicas for list queries
- Conversation pruning (archive old conversations)
- Rate limiting per user

**Alternatives Considered**: Enterprise scale (premature), single-user (not realistic)

---

## MCP Integration Research

### MCP SDK for Python
**Status**: Available via `mcp` package
**Documentation**: https://modelcontextprotocol.io/docs/python-sdk

**Key Concepts**:
- **MCP Server**: Exposes tools that AI can call
- **Tool**: Function with typed input/output schema
- **Transport**: Communication layer (stdio, HTTP, WebSocket)

**Implementation Pattern**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("todo-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="add_task", description="...", inputSchema={...}),
        # ... other tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add_task":
        # call database, return result
        pass
```

**Transport Choice**: HTTP transport for FastAPI integration
**Rationale**: Allows MCP server to run within FastAPI app, sharing database connection pool

---

### OpenAI Agents SDK Integration
**Status**: Available via OpenAI Python SDK 1.10+
**Documentation**: https://platform.openai.com/docs/guides/agents

**Key Concepts**:
- **Agent**: Stateless function that uses tools to accomplish tasks
- **Thread**: Conversation history (stored externally, not in OpenAI)
- **Run**: Single invocation of agent with message history
- **Tools**: Functions agent can call (provided via MCP)

**Implementation Pattern**:
```python
from openai import OpenAI

client = OpenAI()

# Load conversation history from database
messages = [{"role": msg.role, "content": msg.content} for msg in db_messages]

# Create run with MCP tools
run = client.beta.threads.runs.create(
    thread_id=conversation_id,  # our DB conversation ID
    assistant_id=assistant_id,
    additional_messages=[{"role": "user", "content": user_message}],
    tools=[...],  # MCP tools as OpenAI function calling format
)

# Poll for completion and handle tool calls
```

**Strategy**:
- Store conversation history in our database (not OpenAI threads)
- Pass full message history on each request (stateless)
- Convert MCP tool schemas to OpenAI function calling format
- Handle tool calls by invoking MCP server internally

---

### Better Auth Integration
**Status**: Better Auth v1.0+ supports FastAPI
**Documentation**: https://better-auth.com/docs/integrations/fastapi

**Authentication Flow**:
1. User logs in via Better Auth (handled by frontend/auth service)
2. Frontend receives JWT token
3. Frontend sends JWT in Authorization header with each chat request
4. FastAPI middleware validates JWT and extracts user_id
5. API uses user_id for all database operations

**Implementation**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> str:
    # Validate JWT with Better Auth
    # Return user_id
    pass

@app.post("/api/{user_id}/chat")
async def chat(user_id: str, current_user: str = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(403, "Forbidden")
    # ... process chat
```

**Alternatives Considered**: Custom JWT validation (reinventing wheel), no auth (insecure)

---

### ChatKit Frontend Integration
**Status**: OpenAI ChatKit available as React component library
**Documentation**: https://github.com/openai/openai-chatkit

**Configuration**:
```json
{
  "apiUrl": "https://your-api.com/api/{userId}/chat",
  "allowedDomains": ["your-api.com"],
  "theme": "light",
  "initialMessage": "Hello! I can help you manage your tasks. Try saying 'Add task to buy groceries'."
}
```

**Integration Points**:
- ChatKit sends POST requests to API endpoint
- API returns JSON: `{response: string, conversation_id: string}`
- ChatKit maintains conversation_id in localStorage
- ChatKit handles message rendering, input, loading states

**Alternatives Considered**: Custom React chat UI (more work), Streamlit (not suitable for production)

---

## Best Practices

### FastAPI Structure
**Pattern**: Dependency injection for database sessions

```python
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    # session auto-closes after request
```

**Source**: https://fastapi.tiangolo.com/tutorial/dependencies/

---

### SQLModel Async Patterns
**Pattern**: Use async engine with async sessions

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DATABASE_URL, echo=True)

async def get_session():
    async with AsyncSession(engine) as session:
        yield session
```

**Source**: https://sqlmodel.tiangolo.com/advanced/async-sql-databases/

---

### Error Handling
**Pattern**: Custom exception handlers for user-friendly errors

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "conversation_id": request.state.conversation_id}
    )
```

**Source**: https://fastapi.tiangolo.com/tutorial/handling-errors/

---

### Database Migrations
**Pattern**: Alembic for schema migrations

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Rationale**: SQLModel uses SQLAlchemy under the hood, so Alembic works seamlessly

**Source**: https://alembic.sqlalchemy.org/

---

## Unknowns Resolved

All "NEEDS CLARIFICATION" items from Technical Context have been resolved:

✅ Language/Version: Python 3.11+
✅ Primary Dependencies: FastAPI, SQLModel, OpenAI SDK, MCP SDK
✅ Storage: Neon PostgreSQL with asyncpg
✅ Testing: pytest with pytest-asyncio
✅ Target Platform: Linux server (Docker)
✅ Project Type: Web application (backend + frontend)
✅ Performance Goals: < 2s API, < 100ms DB, 100+ concurrent users
✅ Constraints: Stateless, user ID validation, GPT-4o-mini
✅ Scale/Scope: 10-100 users, 1k tasks/user, 50 conversations/user

## Next Steps

Proceed to Phase 1:
1. Create `data-model.md` with entity definitions
2. Generate API contracts in `/contracts/`
3. Create `quickstart.md` for development setup
4. Update agent context with technology stack
