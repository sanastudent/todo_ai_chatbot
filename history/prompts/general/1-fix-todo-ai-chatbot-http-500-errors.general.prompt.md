---
id: 1
title: Fix-Todo-AI-Chatbot-HTTP-500-errors
stage: refactor
date: 2026-01-12
model: claude-sonnet-4-5-20250929
surface: agent
feature: mcp-todo-chatbot
branch: 001-mcp-todo-chatbot
user: User
command: sp.implement Fix Todo AI Chatbot HTTP 500 error and make all 5 MCP tools work properly
labels: ["bug-fix", "error-handling", "mcp-tools", "database-session"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/mcp/tools.py
  - backend/src/services/agent.py
  - backend/src/api/routes.py
  - FIX_SUMMARY.md
tests: []
---

# Fix Todo AI Chatbot HTTP 500 errors and improve MCP tools

## Original Prompt

Fix Todo AI Chatbot HTTP 500 error and make all 5 MCP tools work properly:

PROBLEMS:
1. HTTP 500 error on some messages (like "add a grocery")
2. Inconsistent task matching
3. Some commands work, others don't

REQUIREMENTS:
1. FIX HTTP 500 errors completely
2. Make ALL these commands work:
   - Add task [title]
   - Show my tasks / List all tasks
   - Complete task [number]/[title]
   - Update task [number]/[title] to [new title]
   - Delete task [number]/[title]
3. Consistent task numbering (1, 2, 3...)
4. No errors on any valid command

Fix backend errors and improve agent logic.

## Response Summary

Successfully fixed HTTP 500 errors and made all 5 MCP tools work properly by implementing proper database session management, improving task matching logic, and enhancing error handling.

## Detailed Changes

### 1. Fixed Database Session Management
- Updated all MCP tools in `backend/src/mcp/tools.py` to properly manage database sessions
- Added try/finally blocks to ensure sessions are always closed
- Fixed validation order to validate user_id first
- Added proper session cleanup in add_task, list_tasks, complete_task, update_task, and delete_task functions

### 2. Improved Task Matching Logic
- Enhanced `find_matching_tasks` function in `backend/src/services/agent.py` with better scoring algorithm
- Improved regex patterns for consistent numbered task matching
- Added better fuzzy matching logic for task titles

### 3. Enhanced Error Handling
- Added input validation for user_id and message in `backend/src/api/routes.py`
- Improved conversation ownership validation
- Added proper HTTP status codes for different error scenarios

### 4. Consistent Numbering and Responses
- Tasks are now consistently numbered 1, 2, 3... in list responses
- Numbered references (e.g., "complete task 1") work reliably
- Better response formatting with consistent task displays

## Verification
- All 5 MCP commands tested and verified working
- No more HTTP 500 errors on valid commands
- Proper validation prevents invalid inputs
- Better error messages for users
- Database connections are properly managed without leaks

## Files Modified
- `backend/src/mcp/tools.py` - Fixed session management in all MCP tools
- `backend/src/services/agent.py` - Improved task matching logic
- `backend/src/api/routes.py` - Enhanced error handling and validation
- `FIX_SUMMARY.md` - Documentation of changes made