---
id: PHR-002
title: Fix Quoted Messages Bug
stage: refactor
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: main
user: sanastudent
command: fix-quoted-messages-bug
labels: [bugfix, pattern-matching, frontend-integration]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/services/agent.py
tests:
 - test_quotes_handling.py
---

## Prompt

Fix the issue where frontend sends quoted messages like "\"Add a task...\"" causing pattern matching to fail. The solution involves adding quote stripping at the beginning of the invoke_agent function in backend/src/services/agent.py to handle both single and double quotes.

## Response snapshot

Implemented quote stripping in the invoke_agent function by adding code to remove surrounding quotes from user messages before processing. The fix handles both single quotes ('') and double quotes ("") by checking if the message starts and ends with the same type of quote and removing them if so. This ensures that pattern matching works correctly regardless of how the frontend sends the messages.

## Outcome

- ✅ Impact: Fixed pattern matching failures when frontend sends quoted messages
- 🧪 Tests: Added test case to verify quote stripping functionality works for both single and double quotes
- 📁 Files: Modified backend/src/services/agent.py to add quote stripping logic
- 🔁 Next prompts: Verify the fix works in end-to-end testing
- 🧠 Reflection: The issue occurred because frontend was sending messages with surrounding quotes which interfered with regex pattern matching

## Evaluation notes (flywheel)

- Failure modes observed: Pattern matching failing when messages had surrounding quotes
- Graders run and results (PASS/FAIL): PASS - Pattern matching now works with quoted messages
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor if any edge cases arise with nested quotes
