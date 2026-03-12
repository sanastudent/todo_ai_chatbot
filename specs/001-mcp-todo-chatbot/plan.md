# Implementation Plan: MCP Todo Chatbot

**Branch**: `001-mcp-todo-chatbot` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-todo-chatbot/spec.md`

## Summary

Build an AI-powered chatbot for managing todos through natural language using Model Context Protocol (MCP) architecture. The system will expose task management operations as FastMCP tools that a Gemini agent (via OpenRouter) calls based on user intent parsed from conversational input. All conversation state persists to Neon PostgreSQL database with strict user data isolation. ChatKit-Python/React provides the chat interface with Context7 managing conversation context.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.100+, SQLModel 0.0.14+, FastMCP, ChatKit-Python, OpenRouter SDK
**Storage**: Neon PostgreSQL (Serverless) with asyncpg driver
**Testing**: pytest with pytest-asyncio, httpx for API tests
**Target Platform**: Linux server (Docker containerized)
**Project Type**: Web application (ChatKit-Python backend + ChatKit-React frontend)
**Performance Goals**: API response < 2s p95, database queries < 100ms p95, 100+ concurrent users
**Constraints**: Stateless API design, user ID validation on all requests, Gemini via OpenRouter for cost efficiency
**Scale/Scope**: 10-100 concurrent users, 1k tasks/user, 50 conversations/user, hackathon Phase 3 scope
**Context Management**: Context7 integration for conversation context optimization

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Technical Stack Compliance**
- Python 3.11+: ✅ Mandated by constitution
- FastAPI: ✅ Mandated by constitution
- SQLModel: ✅ Mandated by constitution
- Neon PostgreSQL: ✅ Mandated by constitution
- Gemini (OpenRouter): ✅ Updated tech stack
- FastMCP: ✅ Updated tech stack
- ChatKit-Python: ✅ Updated tech stack
- ChatKit-React: ✅ Updated tech stack
- Context7: ✅ Updated tech stack
- Better Auth: ✅ Mandated by constitution (Phase 5)

✅ **Architecture Requirements**
- FastMCP Server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task): ✅ Matches constitution spec
- Database schema (Task, Conversation, Message): ✅ Matches constitution spec
- Stateless API endpoint `POST /api/{user_id}/chat`: ✅ Matches constitution spec
- User ID validation on every request: ✅ Enforced in design
- Conversation persistence to database: ✅ Part of core design
- Context7 integration for conversation management: ✅ Added for context optimization

✅ **Development Philosophy**
- Spec-Driven Development: ✅ Following SDD-RI process
- Reuse-First Approach: ✅ Using existing ChatKit/FastMCP/Context7, no reinvention
- Stateless Architecture: ✅ All state in database, no server sessions
- MCP-Centric Design: ✅ All task operations via FastMCP tools
- Database as Source of Truth: ✅ PostgreSQL for all persistence
- Context Optimization: ✅ Context7 manages conversation context efficiently

**Result**: ✅ PASS - No constitution violations. All requirements align with mandated stack and architecture.

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-todo-chatbot/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API/MCP contracts
│   ├── api-contract.yaml    # OpenAPI 3.1 spec for REST API
│   └── mcp-tools.json       # MCP tool schemas
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
todo-ai-chatbot/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py          # Task SQLModel
│   │   │   ├── conversation.py  # Conversation SQLModel
│   │   │   └── message.py       # Message SQLModel
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py        # MCP server initialization
│   │   │   └── tools.py         # MCP tool implementations (5 tools)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # FastAPI routes (chat endpoint)
│   │   │   └── deps.py          # Dependencies (auth, db session)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── agent.py         # OpenAI Agents SDK integration
│   │       └── database.py      # Database connection/engine
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_models.py
│   │   │   └── test_mcp_tools.py
│   │   └── integration/
│   │       └── test_api.py      # End-to-end API tests
│   ├── migrations/              # Alembic migration scripts
│   │   ├── env.py
│   │   └── versions/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # ChatKit integration
│   │   └── main.jsx
│   ├── public/
│   ├── chatkit-config.json      # ChatKit configuration
│   ├── package.json
│   └── vite.config.js
├── specs/                       # Feature specifications
├── .specify/                    # SpecKit Plus templates
├── .env                         # Environment variables (gitignored)
├── .gitignore
└── README.md
```

**Structure Decision**: Web application architecture with separate backend and frontend.

**Rationale**:
- **Backend (Python)**: ChatKit-Python with FastAPI + FastMCP tools + Context7
- **Frontend (React)**: ChatKit-React pre-built UI (minimal custom code)
- **AI Layer**: Gemini via OpenRouter for natural language understanding
- **Separation**: Allows independent deployment and scaling
- **Modularity**: Clear boundaries between data models, FastMCP tools, API routes, and services

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All design choices align with constitution requirements. This section intentionally left empty.

## Implementation Overview

### Core Components

1. **Database Layer** ()
   - SQLModel classes for Task, Conversation, Message
   - Alembic migrations for schema management
   - Database indexes for performance

2. **MCP Tools** ()
   - 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
   - User ID validation on all operations
   - Database queries with proper filtering

3. **OpenAI Agent** ()
   - Converts MCP tools to OpenAI function calling format
   - Handles multi-turn tool usage
   - Returns natural language responses

4. **API Endpoint** ()
   - POST /api/{user_id}/chat
   - JWT authentication via Better Auth
   - Conversation persistence logic

5. **Frontend** ()
   - OpenAI ChatKit React component
   - Configuration for backend API URL
   - Minimal custom code

### Development Workflow

1. Set up Neon PostgreSQL database
2. Create database models and run migrations
3. Implement MCP tools with unit tests
4. Build OpenAI agent integration
5. Create FastAPI endpoint with integration tests
6. Configure ChatKit frontend
7. End-to-end testing
8. Deployment

### Key Design Decisions

**Stateless API**: All conversation state in database enables horizontal scaling and server restarts without data loss.

**MCP Architecture**: Separates task operations from AI logic, making tools reusable and testable independently.

**User ID Validation**: Security-first design ensures no cross-user data access at multiple layers (API, MCP tools, database queries).

**GPT-4o-mini**: Cost-efficient model suitable for task management domain (10x cheaper than GPT-4).

---

## Next Steps

**Planning Complete**: All Phase 0 and Phase 1 artifacts generated:
- ✅ research.md - Technology decisions documented
- ✅ data-model.md - Database schema defined
- ✅ contracts/ - API and MCP tool contracts specified
- ✅ quickstart.md - Developer setup guide created
- ✅ plan.md - This implementation plan

**Ready for Task Breakdown**: Run  to generate tasks.md with:
- Dependency-ordered implementation tasks
- Test cases for each task
- Acceptance criteria
- Estimated complexity

**References**:
- [Feature Spec](./spec.md)
- [Research](./research.md)
- [Data Model](./data-model.md)
- [API Contract](./contracts/api-contract.yaml)
- [MCP Tools](./contracts/mcp-tools.json)
- [Quickstart](./quickstart.md)

## Implementation Overview

### Core Components

1. **Database Layer** - SQLModel classes for Task, Conversation, Message with Alembic migrations
2. **FastMCP Tools** - 5 tools with user ID validation and database operations
3. **Gemini Agent** - Gemini via OpenRouter converts FastMCP tools to function calling and handles multi-turn interactions
4. **ChatKit-Python Backend** - POST /api/{user_id}/chat with JWT auth and conversation persistence
5. **ChatKit-React Frontend** - Pre-built React chat UI with minimal configuration
6. **Context7 Integration** - Manages conversation context and optimization

### Key Design Decisions

- **Stateless API**: All conversation state in database enables horizontal scaling
- **FastMCP Architecture**: Separates task operations from AI logic for reusability
- **User ID Validation**: Security-first design prevents cross-user data access
- **Gemini via OpenRouter**: Cost-efficient model for task management domain with flexible routing
- **Context7**: Optimizes conversation context to reduce token usage and improve response quality
- **ChatKit Integration**: Leverages pre-built chat UI components for faster development

---

## Next Steps

**Planning Complete** - All Phase 0 and Phase 1 artifacts generated:
- ✅ research.md - Technology decisions documented
- ✅ data-model.md - Database schema defined  
- ✅ contracts/ - API and MCP tool contracts specified
- ✅ quickstart.md - Developer setup guide created
- ✅ plan.md - This implementation plan

**Ready for Task Breakdown**: Run `/sp.tasks` to generate tasks.md

**References**: [spec.md](./spec.md) | [research.md](./research.md) | [data-model.md](./data-model.md) | [contracts/](./contracts/)
