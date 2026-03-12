---
id: 006
title: Command Parser Fallback Fix
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 003-openrouter-auth-fix
branch: 003-openrouter-auth-fix
user: User
command: /sp.implement
labels: ["critical-bug", "command-parser", "fallback-mode", "error-handling", "exception-flow"]
links:
  spec: specs/003-openrouter-auth-fix/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/agent.py
  - COMMAND_PARSER_FALLBACK_FIX.md
tests:
  - Command parser fallback (PASS)
  - Add task command (PASS)
  - Add task with extra words (PASS)
  - Show my tasks command (PASS)
  - Complete task command (PASS)
  - Original user command "add buy fresh fruits to the tasks" (PASS)
---

## Prompt

**CRITICAL ISSUE:**
The system is now 100% dependent on AI and completely bypasses the command parser. Even simple commands like "add buy fresh fruits" that should work in fallback mode are failing.

**Problem Context:**
All commands were returning: "The AI service is not properly configured. Please check the API key settings."

The command parser was never invoked, even though it was implemented in the previous session.

**Code Analysis Needed:**
1. Where is the "AI service is not properly configured" error coming from?
2. Why is the command parser being bypassed?
3. Check the fallback flow - when AI fails, does it call `parse_basic_commands()`?

**Expected Problematic Pattern:**
```python
try:
    # Try AI processing
    result = await self.client.chat.completions.create(...)
except Exception as e:
    # BUG: Returns error instead of falling back to command parser
    return "The AI service is not properly configured..."
```

## Response snapshot

### Critical Bug Fixed - Command Parser Fallback Now Working

I identified and fixed the critical bug that was preventing the command parser from being invoked as a fallback when AI failed.

#### 🔍 Root Cause Analysis

**Bug Location**: `backend/src/services/agent.py`, function `call_openai_agent()` (lines 550-578)

**The Problem**:
The error handling code was catching exceptions and returning error messages instead of re-raising them. This prevented the fallback mechanism from working.

**Problematic Code**:
```python
except Exception as e:
    error_msg = str(e)
    error_str = error_msg.lower()
    if 'quota' in error_str or 'rate' in error_str:
        return "I'm currently experiencing high demand..."
    elif 'authentication' in error_str or 'invalid' in error_str:  # ← BUG
        return "The AI service is not properly configured..."
    elif 'cookie auth' in error_str:
        return "There's an authentication issue..."
    else:
        raise
```

**Why It Failed**:
1. OpenRouter returned 400 error: "Invalid parameter: messages with role 'tool'..."
2. Error message contained the word "Invalid"
3. Matched the check: `'invalid' in error_str` → True
4. Returned error message instead of raising exception
5. `invoke_agent()` never caught an exception, so never called `mock_ai_response()`
6. Command parser in `mock_ai_response()` → `parse_basic_command()` was never invoked

**The Flow That Should Happen**:
```
User sends command
    ↓
invoke_agent() tries AI
    ↓
AI fails with exception
    ↓
Exception is raised to invoke_agent()
    ↓
invoke_agent() catches exception
    ↓
invoke_agent() calls mock_ai_response()
    ↓
mock_ai_response() calls parse_basic_command()
    ↓
Command parser executes the command
    ↓
User gets result
```

#### ✅ The Fix

**Changed Code** (lines 550-578):
```python
except Exception as e:
    error_msg = str(e)
    logger.error(f"Error calling OpenAI agent: {error_msg}")
    logger.error(f"Error type: {type(e).__name__}")

    # Log API key info for debugging
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        logger.error(f"API Key is set: True, starts with 'sk-or-': {api_key.startswith('sk-or-')}")

    # Re-raise all errors to let invoke_agent() handle fallback to command parser
    # This ensures the command parser is always tried when AI fails
    raise
```

**Why This Works**:
1. All exceptions are re-raised (no conditional returns)
2. Exception propagates to `invoke_agent()`
3. `invoke_agent()` catches it and calls `mock_ai_response()`
4. `mock_ai_response()` calls `parse_basic_command()`
5. Command is executed and result is returned

#### 📊 Test Results

**✅ All Critical Commands Working**:

**Test 1: Add Task**
```bash
Input: "add buy fresh fruits"
Output: "✅ Task added: 'buy fresh fruits'"
Status: ✅ PASS
```

**Test 2: Add Task with Extra Words (Original User Request)**
```bash
Input: "add buy fresh fruits to the tasks"
Output: "✅ Task added: 'buy fresh fruits'"
Status: ✅ PASS
```

**Test 3: Show My Tasks**
```bash
Input: "show my tasks"
Output: "📋 Your tasks:\n\n1. ⬜ buy oranges (ID: d400f90f...)\n2. ⬜ Buy Oranges (ID: a994fec6...)\n..."
Status: ✅ PASS
```

**Test 4: Complete Task**
```bash
Input: "complete task 1"
Output: "✅ Completed: 'buy oranges'\n\nGreat job! Type 'list tasks' to see your remaining tasks."
Status: ✅ PASS
```

#### 🎯 Impact Assessment

**Before Fix**:
- ❌ Command parser never invoked
- ❌ All commands failed with "AI service is not properly configured"
- ❌ System completely unusable when AI had errors
- ❌ User's original request not addressed

**After Fix**:
- ✅ Command parser invoked as fallback when AI fails
- ✅ Add commands work perfectly
- ✅ Complete task commands work
- ✅ Show my tasks works
- ✅ **User's original request is fully resolved**
- ✅ System is now robust and usable

#### 📁 Files Modified

**1. backend/src/services/agent.py**
- Lines 550-578: Simplified error handling to always re-raise exceptions
- Before: 28 lines of complex error checking
- After: 11 lines that always re-raise
- Impact: Critical - enables command parser fallback

**2. COMMAND_PARSER_FALLBACK_FIX.md**
- Comprehensive documentation of the bug, fix, and test results
- Includes root cause analysis and flow diagrams

#### 🔄 Additional Fixes Applied

**Fixed List Tasks Bug**:
- Line 275: Changed `task.get('id', '')` to `task.get('task_id', '')`
- This was causing list tasks to fail when displaying task IDs

## Outcome

- ✅ Impact: **CRITICAL BUG FIXED** - Command parser fallback now works correctly
- 🧪 Tests: All critical commands passing (add, show, complete)
- 📁 Files: Modified 1 file (backend/src/services/agent.py), created 1 documentation file
- 🔁 Next prompts: System is now fully functional in fallback mode
- 🧠 Reflection: This was a critical architectural bug where error handling was preventing the fallback mechanism from working. The fix was simple but had massive impact - changing from conditional error returns to always re-raising exceptions. This ensures the command parser is always tried when AI fails, making the system robust and usable even when AI has issues. The user's original request "add buy fresh fruits to the tasks" now works perfectly.

## Evaluation notes (flywheel)

- Failure modes observed: Error handling was too aggressive, catching and returning errors instead of letting them propagate to the fallback mechanism
- Graders run and results (PASS/FAIL): Add task (PASS), Add with extra words (PASS), Show tasks (PASS), Complete task (PASS), Original user command (PASS)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): System is now working correctly; no further experiments needed for this issue
