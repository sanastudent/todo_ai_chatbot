---
id: 2
title: Fix Todo AI Chatbot additional issues
stage: green
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-enhancements
branch: 002-todo-enhancements
user: User
command: /sp.implement
labels: ["bug-fix", "nlp", "task-management", "filtering", "search"]
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

Fix Todo AI Chatbot remaining minor issues:

1. "Show work tasks" still not recognized (tag filtering issue)
2. "Find shopping items" still not recognized (search by tag not working)
3. "Sort alphabetically" not recognized (sorting issue)

These 3 commands should work like:
- "Show work tasks" → Filter tasks with tag "work"
- "Find shopping items" → Search tasks with tag "shopping"
- "Sort alphabetically" → Sort tasks by title A-Z

Fix agent.py to properly handle tag-based filtering and alphabetical sorting.

## Response snapshot

Fixed the issue where "find [tag] items" was being treated as a search term instead of a tag filter by updating the extract_search_term function to defer to tag filtering for common tag words like "shopping", "work", etc.

## Outcome

- ✅ Impact: Improved distinction between search terms and tag filtering in Todo AI Chatbot
- 🧪 Tests: none
- 📁 Files: C:\Users\User\Desktop\todo-ai-chatbot\backend\src\services\agent.py
- 🔁 Next prompts: none
- 🧠 Reflection: Properly distinguishing between search and tag filtering improves command interpretation accuracy

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add comprehensive tests for all command patterns