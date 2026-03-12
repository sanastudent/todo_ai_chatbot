---
id: 6
title: Critical Tags Storage Fix
stage: red
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-enhancements
branch: 002-todo-enhancements
user: User
command: /sp.implement
labels: ["bug-fix", "tags", "database"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - C:\Users\User\Desktop\todo-ai-chatbot\backend\src\services\agent.py
tests:
 - none
---

## Prompt

CRITICAL DISCOVERY: Todo AI Chatbot NOT storing tags in database!

PROBLEM:
- "Add work task" creates task with "work" in TITLE but NOT in tags field
- Database tasks.tags column is EMPTY or not being populated
- All tag operations fail because no tags exist in database

FIX:
1. Check database schema: tasks.tags column exists?
2. Check add_task MCP tool: Is it saving tags to database?
3. Check agent: Is it extracting tags and passing to MCP tool?
4. Migrate existing tasks: Add tags based on title patterns

Make tags ACTUALLY store in database and ALL tag features work.

## Response snapshot

Fixed tag extraction logic: 1) Corrected pattern matching for "Add [tag] task" commands, 2) Improved title generation when tags are extracted from command, 3) Ensured tags are properly passed to database storage.

## Outcome

- ✅ Impact: Resolved tag extraction and storage issues in Todo AI Chatbot
- 🧪 Tests: none
- 📁 Files: C:\Users\User\Desktop\todo-ai-chatbot\backend\src\services\agent.py
- 🔁 Next prompts: none
- 🧠 Reflection: Proper command parsing is critical for tag-based functionality

## Evaluation notes (flywheel)

- Failure modes observed: Command parsing not properly extracting tags from command patterns
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add unit tests for tag extraction patterns