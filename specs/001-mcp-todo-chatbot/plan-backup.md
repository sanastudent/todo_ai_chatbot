# Implementation Plan: MCP Todo Chatbot

**Branch**: `001-mcp-todo-chatbot` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-todo-chatbot/spec.md`

## Summary

Build an AI-powered chatbot for managing todos through natural language using Model Context Protocol (MCP) architecture. The system will expose task management operations as MCP tools that an OpenAI agent calls based on user intent parsed from conversational input. All conversation state persists to Neon PostgreSQL database with strict user data isolation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.100+, SQLModel 0.0.14+, OpenAI Python SDK 1.10+, MCP SDK
**Storage**: Neon PostgreSQL (Serverless) with asyncpg driver
**Testing**: pytest with pytest-asyncio, httpx for API tests
**Target Platform**: Linux server (Docker containerized)
**Project Type**: Web application (Python backend API + OpenAI ChatKit frontend)
**Performance Goals**: API response < 2s p95, database queries < 100ms p95, 100+ concurrent users
**Constraints**: Stateless API design, user ID validation on all requests, GPT-4o-mini for cost efficiency
**Scale/Scope**: 10-100 concurrent users, 1k tasks/user, 50 conversations/user, hackathon Phase 3 scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Technical Stack Compliance**
- Python 3.11+: ✅ Mandated by constitution
- FastAPI: ✅ Mandated by constitution
- SQLModel: ✅ Mandated by constitution
- Neon PostgreSQL: ✅ Mandated by constitution
- OpenAI Agents SDK: ✅ Mandated by constitution
- MCP SDK: ✅ Mandated by constitution
- Better Auth: ✅ Mandated by constitution (Phase 5)
- ChatKit frontend: ✅ Mandated by constitution

✅ **Architecture Requirements**
- MCP Server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task): ✅ Matches constitution spec
- Database schema (Task, Conversation, Message): ✅ Matches constitution spec
- Stateless API endpoint `POST /api/{user_id}/chat`: ✅ Matches constitution spec
- User ID validation on every request: ✅ Enforced in design
- Conversation persistence to database: ✅ Part of core design

✅ **Development Philosophy**
- Spec-Driven Development: ✅ Following SDD-RI process
- Reuse-First Approach: ✅ Using existing OpenAI/MCP SDKs, no reinvention
- Stateless Architecture: ✅ All state in database, no server sessions
- MCP-Centric Design: ✅ All task operations via MCP tools
- Database as Source of Truth: ✅ PostgreSQL for all persistence

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
- **Backend (Python)**: FastAPI server exposing REST API + MCP tools
- **Frontend (React)**: OpenAI ChatKit pre-built UI (minimal custom code)
- **Separation**: Allows independent deployment and scaling
- **Modularity**: Clear boundaries between data models, MCP tools, API routes, and services

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All design choices align with constitution requirements. This section intentionally left empty.
