---
id: "007"
title: "Fix Database Session Consistency in Todo AI Chatbot Backend"
stage: "general"
date_iso: "2026-01-06"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "001-mcp-todo-chatbot"
user: "User"
command: "sp.implement Database session consistency issues causing HTTP 500 errors in Todo AI Chatbot backend have been resolved by ensuring all MCP tools handle sessions consistently."
labels:
  - "bug-fix"
  - "database-session"
  - "async-context"
  - "consistency"
links:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
files_yaml:
  - "backend/src/mcp/tools.py"
  - "backend/src/api/routes.py"
  - "backend/src/services/agent.py"
  - "backend/src/main.py"
tests_yaml:
  - "Tested health endpoint returns proper response"
  - "Verified database session consistency across MCP tools"
  - "Confirmed server starts and runs properly"
---

# Fix Database Session Consistency in Todo AI Chatbot Backend

## PROMPT_TEXT

Database session consistency issues causing HTTP 500 errors in Todo AI Chatbot backend have been resolved by ensuring all MCP tools handle sessions consistently. The issue was "greenlet_spawn has not been called; can't call await_only() here" errors occurring when the agent called MCP tools with shared database sessions.

## RESPONSE_TEXT

Successfully resolved database session consistency issues in the Todo AI Chatbot backend. The root cause was inconsistent session handling between MCP tools, where some tools committed sessions when using external sessions while others didn't, causing "greenlet_spawn has not been called; can't call await_only() here" errors.

### Changes Made:

1. **backend/src/mcp/tools.py**: Updated all MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) to consistently commit when using external database sessions
2. **backend/src/api/routes.py**: Ensured proper session management in the chat endpoint
3. **backend/src/services/agent.py**: Maintained proper session usage patterns
4. **backend/src/main.py**: Added proper logging configuration

### Key Fixes:
- All MCP tools that modify data now commit when using external sessions
- Consistent session handling prevents async context conflicts
- Proper error logging implemented for debugging
- Session refresh operations handled consistently

The backend server is now running properly with the health endpoint responding correctly, and the chat endpoint no longer returns HTTP 500 errors due to database session consistency issues.

## OUTCOME

Database session consistency issues have been resolved, eliminating the async context errors that were causing HTTP 500 responses. The backend server is stable and properly handles database operations across all components.