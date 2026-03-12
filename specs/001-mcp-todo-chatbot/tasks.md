# Implementation Tasks: MCP Todo Chatbot

**Feature**: 001-mcp-todo-chatbot
**Branch**: `001-mcp-todo-chatbot`
**Date**: 2026-01-03
**Status**: Ready for Implementation

---

## Overview

This document breaks down the implementation into dependency-ordered, independently testable tasks organized by user story. Each user story represents a complete, valuable increment that can be developed and tested in isolation.

### User Story Priorities

From spec.md:
- **P1**: US1 (Add Task), US2 (List Tasks), US6 (Conversation Persistence)
- **P2**: US3 (Complete Task)
- **P3**: US4 (Update Task), US5 (Delete Task)

### MVP Recommendation

**Minimum Viable Product**: US6 (Conversation Persistence) + US1 (Add Task) + US2 (List Tasks)

This provides complete value: users can have conversations, add tasks, and view their tasks. This proves the core architecture (FastMCP + Gemini (OpenRouter) + ChatKit + Context7 + conversation persistence) works end-to-end.

---

## Phase 1: Setup & Infrastructure

**Goal**: Project initialization and development environment

**Duration**: ~1-2 hours

### Tasks

- [X] T001 Create backend directory structure per plan.md (backend/src/{models,mcp,api,services}, backend/tests/{unit,integration})
- [X] T002 Create frontend directory structure per plan.md (frontend/src/, frontend/public/)
- [X] T003 [P] Create backend/requirements.txt with dependencies (fastapi>=0.100.0, sqlmodel>=0.0.14, asyncpg>=0.29.0, fastmcp>=0.1.0, chatkit-python>=0.1.0, openrouter>=0.1.0, context7>=0.1.0, python-dotenv>=1.0.0, uvicorn[standard]>=0.23.0, alembic>=1.12.0)
- [X] T004 [P] Create backend/.env.example with template (DATABASE_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL, CONTEXT7_API_KEY, API_HOST, API_PORT, CORS_ORIGINS, ENVIRONMENT, LOG_LEVEL)
- [X] T005 [P] Create backend/Dockerfile with Python 3.11 base image
- [X] T006 [P] Create .gitignore with Python/Node patterns (*.pyc, __pycache__/, venv/, .env, node_modules/, dist/)
- [X] T007 [P] Create frontend/package.json with dependencies (react, react-dom, vite, chatkit-react)
- [ ] T008 Install backend dependencies in virtual environment (python -m venv venv && pip install -r backend/requirements.txt)
- [ ] T009 Install frontend dependencies (cd frontend && npm install)
- [X] T010 Verify project structure matches plan.md (ls -R backend/ frontend/ and compare)

**Acceptance Criteria**:
- ✅ Directory structure matches plan.md exactly
- ✅ All dependencies install without errors
- ✅ .gitignore prevents sensitive files from being committed

---

## Phase 2: Foundational Layer (Blocking for all User Stories)

**Goal**: Database models, migrations, and core infrastructure that all user stories depend on

**Duration**: ~2-3 hours

**Why separate phase**: These are blocking prerequisites. All user stories require database persistence and the base API structure.

### Database Models

- [ ] T011 [P] Create backend/src/models/__init__.py (empty file)
- [ ] T012 [P] Create Task model in backend/src/models/task.py per data-model.md (id, user_id, title, description, completed, created_at, updated_at)
- [ ] T013 [P] Create Conversation model in backend/src/models/conversation.py per data-model.md (id, user_id, created_at, updated_at)
- [ ] T014 [P] Create Message model in backend/src/models/message.py per data-model.md (id, user_id, conversation_id, role, content, created_at)
- [ ] T015 Export all models from backend/src/models/__init__.py (from .task import Task; from .conversation import Conversation; from .message import Message)

### Database Setup

- [ ] T016 Create backend/src/services/__init__.py (empty file)
- [ ] T017 Create database connection engine in backend/src/services/database.py (async engine with asyncpg, connection pool config)
- [ ] T018 Initialize Alembic in backend/ directory (alembic init migrations)
- [ ] T019 Configure Alembic env.py to use SQLModel models (import models, set target_metadata)
- [ ] T020 Generate initial migration in backend/migrations/versions/ (alembic revision --autogenerate -m "Initial schema: Task, Conversation, Message")
- [ ] T021 Verify migration SQL creates correct tables and indexes per data-model.md (review migration file)
- [ ] T022 Apply migration to development database (alembic upgrade head)
- [ ] T023 Verify database schema with psql or GUI tool (check tables: task, conversation, message with correct columns and indexes)

### Core API Infrastructure

- [ ] T024 Create backend/src/api/__init__.py (empty file)
- [ ] T025 Create backend/src/main.py with FastAPI app initialization (CORS middleware, health endpoint)
- [ ] T026 Create health check endpoint GET /health in backend/src/main.py (returns {"status": "healthy", "timestamp": utcnow})
- [ ] T027 Test health endpoint with curl (curl http://localhost:8000/health)

**Acceptance Criteria**:
- ✅ All 3 models defined with correct fields per data-model.md
- ✅ Database migration creates tables with correct schemas
- ✅ Health endpoint returns 200 OK
- ✅ Database connection works (health check can query DB)

**Independent Test**: Run `alembic upgrade head` and verify 3 tables exist with `\dt` in psql.

---

## Phase 3: User Story 6 - Conversation Persistence (P1)

**Goal**: As a user, I want my chat history to be saved so that when I return to the app, I can see my previous interactions and maintain context across sessions.

**Why this priority**: This is foundational infrastructure that all other stories depend on. Without conversation persistence, the chatbot can't maintain context across requests.

**Duration**: ~3-4 hours

### Tasks

- [X] T028 [US6] Create Pydantic request/response schemas in backend/src/api/schemas.py (ChatRequest, ChatResponse per api-contract.yaml)
- [X] T029 [US6] Create database dependency in backend/src/api/deps.py (get_db_session yields async session)
- [X] T030 [US6] Create stub auth dependency in backend/src/api/deps.py (get_current_user returns user_id from path for now, TODO: Better Auth)
- [X] T031 [US6] Create POST /api/{user_id}/chat endpoint in backend/src/api/routes.py (stub that returns echo response)
- [X] T032 [US6] Implement conversation loading logic in backend/src/api/routes.py (query Conversation by id and user_id)
- [X] T033 [US6] Implement conversation creation logic in backend/src/api/routes.py (create new Conversation if conversation_id not provided)
- [X] T034 [US6] Implement user message persistence in backend/src/api/routes.py (insert Message with role='user')
- [X] T035 [US6] Implement assistant message persistence in backend/src/api/routes.py (insert Message with role='assistant' after agent response)
- [X] T036 [US6] Implement message history loading in backend/src/api/routes.py (query Messages by conversation_id ordered by created_at)
- [X] T037 [US6] Add user_id validation in backend/src/api/routes.py (verify path user_id matches authenticated user from dep)
- [X] T038 [US6] Add error handling for database failures in backend/src/api/routes.py (try/except with HTTPException)
- [ ] T039 [US6] Test conversation creation with curl (POST /api/test-user/chat {"message": "hello"} returns conversation_id)
- [ ] T040 [US6] Test conversation continuation with curl (POST /api/test-user/chat {"message": "hi again", "conversation_id": "..."} uses same conversation)
- [ ] T041 [US6] Test message persistence (query database: SELECT * FROM message WHERE conversation_id=... shows both user and assistant messages)
- [ ] T042 [US6] Test user_id validation (POST /api/different-user/chat with authenticated as test-user returns 403)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has previous conversation → returns to app → conversation history loads and displays previous messages
- ✅ **AC2**: User sends message → message processed → both user message and AI response persisted to database
- ✅ **AC3**: User starts new conversation (no conversation_id) → system creates new conversation and returns conversation_id
- ✅ **AC4**: Database save fails → system returns error to user but does not lose in-memory response

**Independent Test**: Send 3 messages to create a conversation, query database for messages, restart server, send message with same conversation_id, verify all 4 messages present.

**Delivers Value**: Users can have persistent chat conversations. Foundation for all task management features.

---

## Phase 4: User Story 1 - Add Task via Natural Language (P1)

**Goal**: As a user, I want to add tasks by typing natural language commands like "Add task to buy groceries" so that I can quickly capture tasks without learning specific syntax.

**Duration**: ~3-4 hours

**Dependencies**: Requires US6 (conversation persistence) to be complete.

### Tasks

- [X] T043 [US1] Create backend/src/mcp/__init__.py (empty file)
- [X] T044 [US1] Implement add_task FastMCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, title, description?; output: task_id, title, created_at)
- [X] T045 [US1] Add user_id validation in add_task tool (verify user_id matches task ownership before insert)
- [X] T046 [US1] Add input validation in add_task tool (title non-empty, description max 2000 chars)
- [X] T047 [US1] Add error handling in add_task tool (database errors, validation errors)
- [X] T048 [US1] Test add_task tool directly with mock database (call tool function, verify Task inserted with correct fields)
- [X] T049 [US1] Create backend/src/mcp/server.py to initialize FastMCP server (FastMCP instance with add_task tool registered)
- [X] T050 [US1] Create backend/src/services/agent.py with Gemini (OpenRouter) agent integration (convert FastMCP tools to function calling format)
- [X] T051 [US1] Implement invoke_agent function in backend/src/services/agent.py (load conversation history, optimize with Context7, call Gemini via OpenRouter with tools, handle tool calls)
- [X] T052 [US1] Integrate invoke_agent into POST /api/{user_id}/chat endpoint (replace stub response with agent call, add Context7 optimization)
- [ ] T053 [US1] Test agent integration with "Add task to buy groceries" (verify AI calls add_task tool and returns confirmation)
- [ ] T054 [US1] Test task appears in database (SELECT * FROM task WHERE user_id=... shows created task)
- [ ] T055 [US1] Test error handling: empty task title (AI responds with "What task would you like to add?")
- [ ] T056 [US1] Test error handling: database failure (AI responds with user-friendly error message)


## Phase 5: User Story 2 - List Tasks with Filters (P1)

**Goal**: As a user, I want to view my tasks by asking questions like "Show my pending tasks" or "What do I need to do today?" so that I can quickly understand my workload.

**Duration**: ~2-3 hours

**Dependencies**: Requires US6 (conversation persistence) and US1 (task creation) to be complete.

### Tasks

- [X] T057 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, completed?; output: tasks array)
- [X] T058 [US2] Add user_id filtering in list_tasks tool (WHERE user_id = ?)
- [X] T059 [US2] Add completed filtering in list_tasks tool (if completed param provided: WHERE completed = ?)
- [X] T060 [US2] Add sorting in list_tasks tool (ORDER BY created_at DESC for newest first)
- [X] T061 [US2] Test list_tasks tool with pre-populated data (insert test tasks, call tool, verify correct tasks returned)
- [X] T062 [US2] Register list_tasks tool in backend/src/mcp/server.py (add to MCP server tools list)
- [X] T063 [US2] Update OpenAI agent in backend/src/services/agent.py to include list_tasks in function calling
- [ ] T064 [US2] Test "Show my pending tasks" with agent (verify AI calls list_tasks with completed=false)
- [ ] T065 [US2] Test "What's on my todo list?" with agent (verify AI calls list_tasks with no filter)
- [ ] T066 [US2] Test empty task list (no tasks for user → AI responds "You have no tasks yet")
- [ ] T067 [US2] Test task list formatting (10+ tasks → AI returns readable format, not overwhelming)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has 5 pending + 3 completed tasks → asks "Show pending tasks" → AI returns only 5 pending tasks
- ✅ **AC2**: User has multiple tasks → asks "What's on my todo list?" → AI returns all tasks (pending and completed)
- ✅ **AC3**: User has no tasks → asks "Show my tasks" → AI responds "You have no tasks yet"
- ✅ **AC4**: User has 10+ tasks → asks "Show tasks" → AI returns tasks in readable format

**Independent Test**: Pre-populate database with 5 pending and 3 completed tasks, ask "Show pending tasks", verify only pending tasks returned.

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User authenticated → sends "Add task to buy groceries" → AI creates task with title "buy groceries" and returns confirmation
- ✅ **AC2**: User sends "Add buy milk and pick up dry cleaning" → AI creates single task or prompts for clarification
- ✅ **AC3**: User sends "Remind me to call doctor tomorrow at 2pm" → AI creates task with title "call doctor" and description with time reference
- ✅ **AC4**: Task creation fails (DB error) → AI responds with user-friendly error and suggests retry

**Independent Test**: Start with empty task table, send "Add task to buy groceries", verify task exists in database with correct title and user_id.

**Delivers Value**: Users can create tasks conversationally. This is the core value proposition.

---

## Phase 5: User Story 2 - List Tasks with Filters (P1)

**Goal**: As a user, I want to view my tasks by asking questions like "Show my pending tasks" or "What do I need to do today?" so that I can quickly understand my workload.

**Duration**: ~2-3 hours

**Dependencies**: Requires US6 (conversation persistence) and US1 (task creation) to be complete.

### Tasks

- [ ] T057 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, completed?; output: tasks array)
- [ ] T058 [US2] Add user_id filtering in list_tasks tool (WHERE user_id = ?)
- [ ] T059 [US2] Add completed filtering in list_tasks tool (if completed param provided: WHERE completed = ?)
- [ ] T060 [US2] Add sorting in list_tasks tool (ORDER BY created_at DESC for newest first)
- [ ] T061 [US2] Test list_tasks tool with pre-populated data (insert test tasks, call tool, verify correct tasks returned)
- [ ] T062 [US2] Register list_tasks tool in backend/src/mcp/server.py (add to MCP server tools list)
- [ ] T063 [US2] Update OpenAI agent in backend/src/services/agent.py to include list_tasks in function calling
- [ ] T064 [US2] Test "Show my pending tasks" with agent (verify AI calls list_tasks with completed=false)
- [ ] T065 [US2] Test "What's on my todo list?" with agent (verify AI calls list_tasks with no filter)
- [ ] T066 [US2] Test empty task list (no tasks for user → AI responds "You have no tasks yet")
- [ ] T067 [US2] Test task list formatting (10+ tasks → AI returns readable format, not overwhelming)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has 5 pending + 3 completed tasks → asks "Show pending tasks" → AI returns only 5 pending tasks
- ✅ **AC2**: User has multiple tasks → asks "What's on my todo list?" → AI returns all tasks (pending and completed)
- ✅ **AC3**: User has no tasks → asks "Show my tasks" → AI responds "You have no tasks yet"
- ✅ **AC4**: User has 10+ tasks → asks "Show tasks" → AI returns tasks in readable format

**Independent Test**: Pre-populate database with 5 pending and 3 completed tasks, ask "Show pending tasks", verify only pending tasks returned.

**Delivers Value**: Users can review their task list conversationally. Completes the basic read/write cycle with US1.

---

## Phase 6: User Story 3 - Complete Task (P2)

**Goal**: As a user, I want to mark tasks as done by saying "Complete task: buy groceries" or "Mark buy groceries as done" so that I can track progress.

**Duration**: ~2 hours

**Dependencies**: Requires US1 (task creation) and US2 (task listing) to be complete.

### Tasks

- [X] T068 [US3] Implement complete_task MCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, task_id; output: task_id, completed, updated_at)
- [X] T069 [US3] Add user_id validation in complete_task tool (verify task belongs to user before update)
- [X] T070 [US3] Add task existence check in complete_task tool (return NOT_FOUND if task doesn't exist)
- [X] T071 [US3] Add idempotency check in complete_task tool (if already completed, return success with message "Task already completed")
- [X] T072 [US3] Update completed=true and updated_at timestamp in complete_task tool
- [X] T073 [US3] Test complete_task tool with mock database (create pending task, call tool, verify completed=true)
- [X] T074 [US3] Register complete_task tool in backend/src/mcp/server.py
- [X] T075 [US3] Update OpenAI agent in backend/src/services/agent.py to include complete_task
- [ ] T076 [US3] Test "Complete buy groceries" with agent (create task, complete it, verify status changes)
- [ ] T077 [US3] Test non-existent task completion (AI responds "Could not find task")
- [ ] T078 [US3] Test already completed task (AI responds "Task already completed")
- [ ] T079 [US3] Test completed task no longer shows in pending list (list_tasks with completed=false excludes it)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has pending task "buy groceries" → says "Complete buy groceries" → AI marks completed and confirms
- ✅ **AC2**: User has multiple similar task names → says "Complete task X" → AI completes exact match or asks clarification
- ✅ **AC3**: User references non-existent task → AI responds "Could not find task Y"
- ✅ **AC4**: Task already completed → user tries again → AI responds "Task already completed"

**Independent Test**: Create task "buy groceries", complete it, verify completed=true in database and task doesn't appear in pending list.

**Delivers Value**: Users can mark tasks as done, completing the basic task lifecycle (create, view, complete).

---

## Phase 7: User Story 4 - Update Task Details (P3)

**Goal**: As a user, I want to update task titles or descriptions by saying "Change buy groceries to buy organic groceries" so that I can refine tasks as my plans change.

**Duration**: ~2 hours

**Dependencies**: Requires US1 (task creation) to be complete.

### Tasks

- [ ] T080 [US4] Implement update_task MCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, task_id, title?, description?; output: task_id, updated_fields, updated_at)
- [ ] T081 [US4] Add user_id validation in update_task tool (verify task belongs to user)
- [ ] T082 [US4] Add task existence check in update_task tool (return NOT_FOUND if doesn't exist)
- [ ] T083 [US4] Add field validation in update_task tool (at least one field must be provided, title non-empty if provided)
- [ ] T084 [US4] Update task fields and updated_at timestamp in update_task tool
- [ ] T085 [US4] Test update_task tool with mock database (update title, verify change persisted)
- [ ] T086 [US4] Register update_task tool in backend/src/mcp/server.py
- [ ] T087 [US4] Update OpenAI agent in backend/src/services/agent.py to include update_task
- [ ] T088 [US4] Test "Update buy groceries to buy organic groceries" with agent (verify title updated)
- [ ] T089 [US4] Test "Add note to call doctor: Ask about prescription" with agent (verify description updated)
- [ ] T090 [US4] Test non-existent task update (AI responds "Could not find that task")
- [ ] T091 [US4] Test updated task shows in list with new title (list_tasks returns updated title)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has task "buy groceries" → says "Update buy groceries to buy organic groceries" → AI updates title and confirms
- ✅ **AC2**: User has task "call doctor" → says "Add note to call doctor: Ask about prescription refill" → AI updates description
- ✅ **AC3**: User references non-existent task → AI responds "Could not find that task"

**Independent Test**: Create task "buy groceries", update to "buy organic groceries", verify title changed in database and list query.

**Delivers Value**: Users can refine tasks as plans change. Nice-to-have for MVP but valuable for user experience.

---

## Phase 8: User Story 5 - Delete Task (P3)

**Goal**: As a user, I want to remove tasks by saying "Delete buy groceries" so that I can clean up my task list when items become irrelevant.

**Duration**: ~1-2 hours

**Dependencies**: Requires US1 (task creation) to be complete.

### Tasks

- [ ] T092 [US5] Implement delete_task MCP tool in backend/src/mcp/tools.py per mcp-tools.json (input: user_id, task_id; output: success, task_id)
- [ ] T093 [US5] Add user_id validation in delete_task tool (verify task belongs to user)
- [ ] T094 [US5] Add task existence check in delete_task tool (return NOT_FOUND if doesn't exist)
- [ ] T095 [US5] Delete task from database in delete_task tool (DELETE FROM task WHERE id=? AND user_id=?)
- [ ] T096 [US5] Test delete_task tool with mock database (create task, delete it, verify removed)
- [ ] T097 [US5] Register delete_task tool in backend/src/mcp/server.py
- [ ] T098 [US5] Update OpenAI agent in backend/src/services/agent.py to include delete_task
- [ ] T099 [US5] Test "Delete buy groceries" with agent (create task, delete it, verify removed from database)
- [ ] T100 [US5] Test non-existent task deletion (AI responds "Could not find that task")
- [ ] T101 [US5] Test deleted task doesn't show in list (list_tasks doesn't return deleted task)

**Acceptance Criteria** (from spec.md):
- ✅ **AC1**: User has task "buy groceries" → says "Delete buy groceries" → AI permanently removes task and confirms
- ✅ **AC2**: User references non-existent task → AI responds "Could not find that task"
- ✅ **AC3**: Task deletion is irreversible → AI may optionally ask for confirmation before deleting

**Independent Test**: Create task "buy groceries", delete it, verify it no longer appears in list_tasks and is removed from database.

**Delivers Value**: Users can clean up irrelevant tasks. Completes full CRUD operations on tasks.

---

## Phase 9: Frontend Integration

**Goal**: Set up OpenAI ChatKit frontend to communicate with backend API

**Duration**: ~2-3 hours

**Dependencies**: Requires US6 (chat API endpoint) to be complete.

### Tasks

- [ ] T102 [P] Create frontend/src/App.jsx with ChatKit component import
- [ ] T103 [P] Create frontend/src/main.jsx with React root rendering
- [ ] T104 [P] Create frontend/chatkit-config.json per quickstart.md (apiUrl, allowedDomains, theme, initialMessage)
- [ ] T105 [P] Create frontend/index.html with React root div
- [ ] T106 [P] Create frontend/vite.config.js with dev server config (proxy to backend on port 8000)
- [ ] T107 Configure ChatKit with backend API URL (http://localhost:8000/api/{userId}/chat)
- [ ] T108 Add CORS configuration in backend/src/main.py (allow frontend origin http://localhost:5173)
- [ ] T109 Test frontend loads (npm run dev, visit http://localhost:5173, see chat interface)
- [ ] T110 Test end-to-end: "Add task to buy groceries" from frontend (verify task created in backend DB)
- [ ] T111 Test end-to-end: "Show my tasks" from frontend (verify tasks displayed in chat)

**Acceptance Criteria**:
- ✅ Frontend loads without errors
- ✅ Chat interface is functional
- ✅ Messages sent from frontend reach backend and return responses
- ✅ Task creation and listing work end-to-end

**Independent Test**: Open frontend, send "Add task to buy groceries", then "Show my tasks", verify task appears in response.

**Delivers Value**: Users can interact with the chatbot via a web interface instead of curl.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Goal**: Error handling, logging, documentation, deployment readiness

**Duration**: ~3-4 hours

**Dependencies**: All user stories complete.

### Tasks

- [ ] T112 [P] Add comprehensive error handling in backend/src/api/routes.py (custom exception handlers for HTTPException, validation errors)
- [ ] T113 [P] Add request logging middleware in backend/src/main.py (log request method, path, duration, status)
- [ ] T114 [P] Add structured logging in backend/src/services/ (use logging module, JSON format for production)
- [ ] T115 [P] Create README.md with project overview (feature description, architecture, tech stack)
- [ ] T116 [P] Document API endpoints in README.md (link to api-contract.yaml, example requests)
- [ ] T117 [P] Create deployment guide in README.md (Docker build, environment variables, database setup)
- [ ] T118 [P] Add OpenAPI documentation generation in backend/src/main.py (FastAPI auto-generates /docs and /redoc)
- [ ] T119 Test error scenarios comprehensively (invalid user_id, missing parameters, database down, OpenAI API down)
- [ ] T120 Test concurrent requests (simulate 10 concurrent users, verify no data corruption)
- [ ] T121 Verify all success criteria from spec.md (SC-001 through SC-010)
- [ ] T122 Create deployment Dockerfile (multi-stage build, production dependencies only)
- [ ] T123 Test Docker build and run (docker build -t todo-chatbot ., docker run --env-file .env -p 8000:8000 todo-chatbot)

**Acceptance Criteria**:
- ✅ Error messages are user-friendly and helpful
- ✅ Logs provide debugging information without exposing sensitive data
- ✅ README provides clear setup and deployment instructions
- ✅ API documentation is accessible via /docs
- ✅ Docker image builds and runs successfully

**Delivers Value**: Production-ready application with proper error handling, logging, and documentation.

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
    ├→ Phase 3 (US6: Conversation Persistence) [BLOCKING FOR ALL BELOW]
    │       ↓
    │       ├→ Phase 4 (US1: Add Task)
    │       │       ↓
    │       │       ├→ Phase 5 (US2: List Tasks)
    │       │       ├→ Phase 6 (US3: Complete Task)
    │       │       ├→ Phase 7 (US4: Update Task)
    │       │       └→ Phase 8 (US5: Delete Task)
    │       │
    │       └→ Phase 9 (Frontend Integration)
    │
    └→ Phase 10 (Polish)
```

**Parallel Execution Opportunities**:

After Phase 3 (US6) completes:
- **Parallel Track A**: Phase 4 (US1) → Phase 5 (US2) → Phase 6 (US3)
- **Parallel Track B**: Phase 7 (US4) and Phase 8 (US5) can be done independently
- **Parallel Track C**: Phase 9 (Frontend) can start once US6 is complete

Specific parallel task opportunities:
- **T003-T007** can be done in parallel (different files, no dependencies)
- **T012-T014** can be done in parallel (different model files)
- **T044-T049** (US1 tasks) can have T050-T051 (agent setup) started in parallel
- **T102-T106** (frontend setup) can all be done in parallel

---

## Implementation Strategy

### MVP-First Approach

**MVP = Phase 1-5 (Setup + Foundational + US6 + US1 + US2)**

This delivers complete end-to-end value:
1. Users can have conversations (US6)
2. Users can add tasks (US1)
3. Users can view their tasks (US2)

**Post-MVP Increments**:
- **Increment 1**: Add Phase 6 (US3 - Complete tasks)
- **Increment 2**: Add Phase 7 + 8 (US4/US5 - Update/Delete tasks)
- **Increment 3**: Add Phase 9 (Frontend)
- **Increment 4**: Add Phase 10 (Polish)

### Testing Strategy

Each phase has specific **Independent Test** criteria. Tests are integration tests since spec doesn't explicitly request TDD.

**Manual Testing**:
- Use curl for API testing (examples in quickstart.md)
- Use psql for database verification
- Use frontend for end-to-end testing

**Future Test Automation** (not in current scope):
- Create backend/tests/unit/test_mcp_tools.py with pytest
- Create backend/tests/integration/test_api.py with httpx
- Run tests in CI/CD pipeline

---

## Task Summary

**Total Tasks**: 123

**Breakdown by Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 17 tasks (~27 total)
- Phase 3 (US6): 15 tasks (~42 total)
- Phase 4 (US1): 14 tasks (~56 total)
- Phase 5 (US2): 11 tasks (~67 total)
- Phase 6 (US3): 12 tasks (~79 total)
- Phase 7 (US4): 12 tasks (~91 total)
- Phase 8 (US5): 10 tasks (~101 total)
- Phase 9 (Frontend): 10 tasks (~111 total)
- Phase 10 (Polish): 12 tasks (123 total)

**Parallelizable Tasks**: 28 tasks marked with [P]

**MVP Task Count**: 67 tasks (Phases 1-5)

**Estimated Total Duration**: 20-25 hours (with parallel execution)

---

## Validation Checklist

✅ **Format**: All tasks follow `- [ ] T### [P?] [US#?] Description with file path` format
✅ **User Story Mapping**: All Phase 3-8 tasks have [US#] labels
✅ **Dependencies**: Dependency graph shows clear order of execution
✅ **Independent Tests**: Each user story phase has "Independent Test" section
✅ **File Paths**: All tasks specify exact file locations
✅ **Acceptance Criteria**: Each user story phase maps to spec.md acceptance scenarios
✅ **Parallel Opportunities**: 28 tasks marked as parallelizable
✅ **MVP Clarity**: MVP scope clearly defined (Phases 1-5)

---

## References

- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/api-contract.yaml](./contracts/api-contract.yaml)
- **MCP Tools**: [contracts/mcp-tools.json](./contracts/mcp-tools.json)
- **Quickstart Guide**: [quickstart.md](./quickstart.md)
