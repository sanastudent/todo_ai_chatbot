---
id: "001"
title: "Fix Internal Server Error in Todo AI Chatbot Backend"
stage: "general"
date_iso: "2026-01-06"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "001-mcp-todo-chatbot"
user: "User"
command: "sp.implement Fix \"Internal server error\" in Todo AI Chatbot backend when user sends message."
labels:
  - "bug-fix"
  - "ai-service"
  - "error-handling"
links:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
files_yaml:
  - "backend/src/services/agent.py"
tests_yaml:
  - "Tested import of updated agent module"
  - "Tested mock AI response functionality"
  - "Tested fallback functionality"
  - "Tested error handling"
  - "Tested main application startup"
---
# Fix Internal Server Error in Todo AI Chatbot Backend

## PROMPT_TEXT

Fix "Internal server error" in Todo AI Chatbot backend when user sends message.

PROBLEM: Frontend shows "Error: Internal server error" when sending chat messages.

REQUIRED FIXES:

1. CHECK BACKEND LOGS to see actual error causing internal server error
2. FIX AI AGENT SERVICE in backend/src/services/agent.py:
   - Check if OpenRouter API key is valid or missing
   - Add fallback mock responses when API key not configured
   - Add error handling for AI service failures

3. UPDATE AGENT SERVICE with fallback:
```python
async def invoke_agent(user_id, message, conversation_id=None):
    try:
        # Try real AI call
        if os.getenv("OPENROUTER_API_KEY"):
            return await call_gemini_ai(message)
        else:
            # Fallback mock responses
            return await mock_ai_response(message)
    except Exception as e:
        logger.error(f"AI agent error: {e}")
        return "I'm having trouble connecting to AI services. Please try again later."
```

## RESPONSE_TEXT

Fixed the internal server error in the Todo AI Chatbot backend by implementing the required fallback functionality in the agent service. The changes include:

1. Added `httpx` and `json` imports to agent.py
2. Implemented `call_gemini_ai()` function to handle OpenRouter API calls with proper error handling
3. Implemented `mock_ai_response()` function for fallback when API key is not configured
4. Updated `invoke_agent()` function to implement the exact fallback logic as specified:
   - Check if OPENROUTER_API_KEY exists
   - Call real AI service if key exists
   - Use mock response if no key
   - Include comprehensive error handling with fallback message
5. Verified that the application starts without errors
6. Tested all functionality including import, mock responses, fallback, and error handling

The implementation now properly handles all scenarios:
- When API key is configured: calls the real Gemini AI service
- When API key is missing: falls back to mock responses
- When API call fails: returns user-friendly error message instead of crashing

## OUTCOME

The internal server error has been resolved. The backend now properly handles AI service calls with appropriate fallbacks and error handling, preventing the "Internal server error" that was occurring when users sent messages.