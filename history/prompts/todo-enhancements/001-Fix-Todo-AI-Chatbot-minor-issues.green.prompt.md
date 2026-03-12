---
id: 1
title: Fix Todo AI Chatbot minor issues
stage: green
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-enhancements
branch: 002-todo-enhancements
user: User
command: /sp.implement
labels: ["bug-fix", "nlp", "task-management", "filtering"]
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

Fix Todo AI Chatbot minor issues:

1. **"Show work tasks"** not recognized (but "Add work task" works)
2. **"Find shopping items"** not recognized (but "Add shopping task" works)
3. **Tag filtering** - "Filter by tag shopping" shows all tasks instead of filtering

Fix agent.py to properly recognize tag-based filter commands and improve tag filtering logic.

## Response snapshot

Fixed all three issues in agent.py by updating the list tasks condition to recognize "find [tag] items" pattern and enhancing the extract_tags_filter function to properly handle "show [tag] tasks", "find [tag] items", and "filter by tag [tagname]" patterns.

## Outcome

- ✅ Impact: Resolved three command recognition issues in Todo AI Chatbot for improved user experience
- 🧪 Tests: none
- 📁 Files: C:\Users\User\Desktop\todo-ai-chatbot\backend\src\services\agent.py
- 🔁 Next prompts: none
- 🧠 Reflection: Improved NLP pattern matching in agent.py significantly enhances command recognition accuracy

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add more comprehensive tests for the fixed patterns