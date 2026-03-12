# Todo AI Chatbot Constitution v1.0

## PROJECT IDENTITY
- **Name**: Todo AI Chatbot (Hackathon Phase 3)
- **Mission**: AI-powered chatbot for managing todos through natural language using MCP architecture
- **Core Innovation**: Natural language task management with Model Context Protocol
- **Phase**: Hackathon Phase 3 Implementation

## DEVELOPMENT PHILOSOPHY
1. **Spec-Driven Development**: No code without complete specification
2. **Reuse-First Approach**: Preserve existing TODO agents/skills, wrap with new interfaces
3. **Stateless Architecture**: All state in database, servers hold no conversation state
4. **MCP-Centric Design**: All task operations through MCP tools
5. **Database as Source of Truth**: Neon PostgreSQL for all persistence

## TECHNICAL STACK (MANDATORY)
- **Backend**: Python 3.11+, FastAPI, SQLModel, ChatKit-Python
- **AI Layer**: Gemini (via OpenRouter), FastMCP
- **Database**: Neon PostgreSQL (Serverless)
- **Frontend**: ChatKit-React
- **Authentication**: Better Auth
- **Protocol**: Model Context Protocol (MCP) via FastMCP
- **Context Management**: Context7

## ARCHITECTURE REQUIREMENTS
1. **FastMCP Server**: Must expose 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
2. **Database**: Must have 3 tables: Task, Conversation, Message with proper relationships
3. **API**: Single stateless endpoint `POST /api/{user_id}/chat` that persists conversation to database
4. **AI Agent**: Gemini (via OpenRouter) integration that calls FastMCP tools based on natural language
5. **Frontend**: ChatKit-React interface with domain allowlist configuration
6. **Stateless Design**: Any server instance can handle any request, all state in database
7. **Context Management**: Context7 integration for conversation context optimization

## DATABASE SCHEMA (NON-NEGOTIABLE)
```python
# Task Model
Task(id, user_id, title, description, completed, created_at, updated_at)

# Conversation Model
Conversation(id, user_id, created_at, updated_at)

# Message Model
Message(id, user_id, conversation_id, role(user/assistant), content, created_at)
```

## MCP TOOLS SPECIFICATION
Each tool must be exposed by the MCP server with the following signatures:

### 1. add_task
- **Input**: `{user_id: str, title: str, description?: str}`
- **Output**: `{task_id: str, title: str, created_at: datetime}`
- **Purpose**: Create a new task for the user

### 2. list_tasks
- **Input**: `{user_id: str, completed?: bool}`
- **Output**: `{tasks: Task[]}`
- **Purpose**: Retrieve all tasks (optionally filtered by completion status)

### 3. complete_task
- **Input**: `{user_id: str, task_id: str}`
- **Output**: `{task_id: str, completed: bool, updated_at: datetime}`
- **Purpose**: Mark a task as completed

### 4. delete_task
- **Input**: `{user_id: str, task_id: str}`
- **Output**: `{success: bool, task_id: str}`
- **Purpose**: Permanently delete a task

### 5. update_task
- **Input**: `{user_id: str, task_id: str, title?: str, description?: str}`
- **Output**: `{task_id: str, updated_fields: object, updated_at: datetime}`
- **Purpose**: Update task title or description

## API SPECIFICATION

### Endpoint: POST /api/{user_id}/chat
- **Purpose**: Stateless chat endpoint that processes user messages and returns AI responses
- **Request Body**: `{message: str, conversation_id?: str}`
- **Response**: `{response: str, conversation_id: str, message_id: str}`
- **Behavior**:
  1. Load conversation history from database (if conversation_id provided)
  2. Create new conversation if needed
  3. Persist user message to database
  4. Optimize context with Context7
  5. Invoke Gemini Agent (via OpenRouter) with FastMCP tools
  6. Persist assistant response to database
  7. Return response to client

## NON-FUNCTIONAL REQUIREMENTS
1. **Performance**: API responses < 2s for simple queries
2. **Security**: User ID validation on every request, no cross-user data access
3. **Reliability**: Database connection pooling, retry logic on failures
4. **Scalability**: Stateless design allows horizontal scaling
5. **Testing**: Unit tests for MCP tools, integration tests for API endpoint

## IMPLEMENTATION PHASES
1. **Phase 1**: Database setup (Neon PostgreSQL, SQLModel models)
2. **Phase 2**: FastMCP server implementation (5 tools)
3. **Phase 3**: ChatKit-Python backend with Gemini (OpenRouter) + Context7
4. **Phase 4**: Frontend integration with ChatKit-React
5. **Phase 5**: Authentication with Better Auth

## GOVERNANCE
- All code must follow the specification
- No direct database access from frontend
- All task operations must go through FastMCP tools
- Conversation state must be persisted to database
- Context7 must be used for conversation context optimization
- Constitution supersedes all other practices

**Version**: 1.1 | **Ratified**: 2026-01-03 | **Last Amended**: 2026-01-03
**Amendment Notes**: Updated tech stack to Gemini (OpenRouter), FastMCP, ChatKit-Python/React, and Context7
