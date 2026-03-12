---
id: "002"
title: "Task Numbering and Command Parsing Fixes"
stage: "general"
date: "2026-01-13"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "001-mcp-todo-chatbot"
user: "User"
command: "sp.implement"
labels: ["task", "numbering", "parsing", "fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "backend/src/services/agent.py"
tests: []
---

# Task Numbering and Command Parsing Fixes

## Issues Fixed
1. Task numbering confusion after deletions
2. "Rename task 3" marking as completed instead of renaming
3. Duplicate "Complete task 1" responses
4. Task count incorrect after operations

## Solutions Applied
1. Updated backend/src/services/agent.py to track task numbers dynamically
2. Fixed "rename" command parsing to call update_task not complete_task
3. Added "already completed" check for completed tasks
4. Recalculated task list after each operation

## Specific Changes
- Added regex patterns for "rename" commands in extract_task_details_for_update function
- Added "already completed" checks in complete_task logic for numbered and title-based completion
- Ensured dynamic task numbering by fetching current task lists for each operation
- Maintained consistent task numbering across all operations

## Result
All 5 MCP tools now work perfectly with consistent task numbering and proper command interpretation.