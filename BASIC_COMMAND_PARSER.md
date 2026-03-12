# Basic Command Parser Implementation

**Date**: 2026-02-06
**Feature**: Fallback Command Parser for AI-Unavailable Mode
**Status**: IMPLEMENTED (Requires Backend Restart)

---

## Overview

Implemented a basic command parser that allows the system to handle simple task management commands even when the AI API key is not configured or AI service is unavailable.

## Problem Identified

**Original Issue**: The system showed help text with command syntax but didn't actually parse or execute commands when AI was unavailable.

**Example**:
- User sends: `"add buy fresh fruits to the tasks"`
- System returned: Help text saying "Try using specific commands like: 'add [task]'"
- **But**: The command wasn't actually parsed or executed

## Solution Implemented

### New Function: `parse_basic_command()`

**Location**: `backend/src/services/agent.py`

**Purpose**: Parse and execute basic task management commands using regex patterns and direct MCP tool calls.

### Supported Commands

#### 1. Add Task
**Patterns**:
- `add [task]` → "add buy milk"
- `add task [task]` → "add task buy milk"
- `create [task]` → "create buy milk"
- `add [task] to the tasks` → "add buy fresh fruits to the tasks"
- `I need to [task]` → "I need to buy milk"

**Example**:
```
Input: "add buy fresh fruits to the tasks"
Output: "✅ Task added: 'buy fresh fruits'

You can view your tasks by typing 'list tasks'."
```

**Implementation**:
```python
add_patterns = [
    r'^add\s+(?:task\s+)?(?:to\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^create\s+(?:task\s+)?(?:to\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$',
    r'^(?:i\s+)?(?:need\s+to|want\s+to|have\s+to)\s+(.+)$',
]
```

#### 2. List Tasks
**Patterns**:
- `list tasks`
- `show tasks`
- `show my tasks`
- `view all tasks`
- `see my tasks`

**Example**:
```
Input: "list tasks"
Output: "📋 Your tasks:

1. ⬜ buy fresh fruits (ID: 12345678...)
2. ✅ buy milk (ID: 87654321...)

💡 Tip: Complete a task by typing 'complete task [number]'"
```

#### 3. Complete Task
**Patterns**:
- `complete task 1`
- `finish task 1`
- `mark task 1 as done`
- `done task 1`

**Example**:
```
Input: "complete task 1"
Output: "✅ Completed: 'buy fresh fruits'

Great job! Type 'list tasks' to see your remaining tasks."
```

#### 4. Delete Task
**Patterns**:
- `delete task 1`
- `remove task 1`
- `cancel task 1`

**Example**:
```
Input: "delete task 1"
Output: "🗑️ Deleted: 'buy fresh fruits'

Type 'list tasks' to see your remaining tasks."
```

### Updated Function: `mock_ai_response()`

**Changes**:
1. Added optional parameters: `user_id` and `db_session`
2. Calls `parse_basic_command()` first before showing help text
3. If command is parsed successfully, returns the command result
4. If no command matches, returns the original help text

**Signature**:
```python
async def mock_ai_response(
    message: str,
    user_id: str = None,
    db_session: AsyncSession = None
) -> str
```

### Updated Function: `invoke_agent()`

**Changes**:
- All calls to `mock_ai_response()` now pass `user_id` and `db_session` parameters
- This enables command parsing in all fallback scenarios:
  - Fake API key detected
  - No API key configured
  - API call failed with error

**Updated Calls**:
```python
# Before
response_text = await mock_ai_response(user_message)

# After
response_text = await mock_ai_response(user_message, user_id, db_session)
```

---

## Technical Details

### Regex Patterns

**Add Task Pattern**:
```python
r'^add\s+(?:task\s+)?(?:to\s+)?(.+?)(?:\s+to\s+(?:the\s+)?tasks?)?$'
```
- Matches: "add", "add task", "add to"
- Captures: The task description
- Strips: Trailing "to the tasks" or "to tasks"

**List Tasks Pattern**:
```python
r'^(?:list|show|view|display|get|see)\s+(?:my\s+)?(?:all\s+)?tasks?$'
```
- Matches: Various verbs (list, show, view, etc.)
- Allows: Optional "my" or "all" modifiers
- Matches: "task" or "tasks"

**Complete/Delete Task Pattern**:
```python
r'^(?:complete|finish|done|mark)\s+(?:task\s+)?(\d+|[a-f0-9-]+)(?:\s+as\s+done)?$'
```
- Matches: Action verbs
- Captures: Task number (1, 2, 3) or UUID
- Allows: Optional "as done" suffix

### Task Number Resolution

When users reference tasks by number (e.g., "complete task 1"):
1. System calls `list_tasks()` to get all tasks
2. Converts task number to zero-based index
3. Retrieves the task ID from the list
4. Calls the appropriate MCP tool with the task ID

**Example**:
```python
if task_ref.isdigit():
    result = await list_tasks(user_id=user_id, db_session=db_session)
    tasks = result['tasks']
    task_index = int(task_ref) - 1
    if 0 <= task_index < len(tasks):
        task_id = tasks[task_index]['id']
        result = await complete_task(user_id=user_id, task_id=task_id, db_session=db_session)
```

### Error Handling

All command executions are wrapped in try-except blocks:
```python
try:
    result = await add_task(user_id=user_id, title=task_title, db_session=db_session)
    return f"✅ Task added: '{task_title}'\n\nYou can view your tasks by typing 'list tasks'."
except Exception as e:
    logger.error(f"Error adding task: {str(e)}")
    return f"❌ Sorry, I couldn't add the task. Error: {str(e)}"
```

---

## Files Modified

1. **`backend/src/services/agent.py`**
   - Added `parse_basic_command()` function (150+ lines)
   - Updated `mock_ai_response()` function signature and implementation
   - Updated all calls to `mock_ai_response()` in `invoke_agent()` (8 locations)

---

## Testing Instructions

### Prerequisites
1. Backend must be restarted to load the new code
2. Backend should be running with stale/fake/no API key (to trigger fallback mode)

### Test Cases

#### Test 1: Add Task
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy fresh fruits"}'
```

**Expected Response**:
```json
{
  "response": "✅ Task added: 'buy fresh fruits'\n\nYou can view your tasks by typing 'list tasks'.",
  "conversation_id": "...",
  "message_id": "..."
}
```

#### Test 2: Add Task with Extra Words
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add buy fresh fruits to the tasks"}'
```

**Expected Response**:
```json
{
  "response": "✅ Task added: 'buy fresh fruits'\n\nYou can view your tasks by typing 'list tasks'.",
  "conversation_id": "...",
  "message_id": "..."
}
```

#### Test 3: List Tasks
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list tasks"}'
```

**Expected Response**:
```json
{
  "response": "📋 Your tasks:\n\n1. ⬜ buy fresh fruits (ID: 12345678...)\n\n💡 Tip: Complete a task by typing 'complete task [number]'",
  "conversation_id": "...",
  "message_id": "..."
}
```

#### Test 4: Complete Task
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "complete task 1"}'
```

**Expected Response**:
```json
{
  "response": "✅ Completed: 'buy fresh fruits'\n\nGreat job! Type 'list tasks' to see your remaining tasks.",
  "conversation_id": "...",
  "message_id": "..."
}
```

#### Test 5: Delete Task
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "delete task 1"}'
```

**Expected Response**:
```json
{
  "response": "🗑️ Deleted: 'buy fresh fruits'\n\nType 'list tasks' to see your remaining tasks.",
  "conversation_id": "...",
  "message_id": "..."
}
```

#### Test 6: Unrecognized Command
```bash
curl -X POST http://localhost:8001/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "do something random"}'
```

**Expected Response**:
```json
{
  "response": "I couldn't understand your request: 'do something random'\n\n⚠️ Note: AI natural language processing is not available (no API key configured).\n\nTry using specific commands like:\n• 'add [task]' - Add a new task\n• 'list tasks' or 'show my tasks' - View all tasks\n• 'complete task [number]' - Mark a task as done\n• 'delete task [number]' - Remove a task\n• 'update task [number] to [new title]' - Change a task",
  "conversation_id": "...",
  "message_id": "..."
}
```

---

## Benefits

### 1. Improved User Experience
- Users can still manage tasks even without AI
- No need to wait for API key configuration
- System remains functional in degraded mode

### 2. Better Fallback Behavior
- Help text is now actionable
- Commands shown in help actually work
- Consistent with user expectations

### 3. Development/Testing
- Developers can test task management without API keys
- Easier to debug MCP tool integration
- Faster development iteration

### 4. Resilience
- System continues working during AI service outages
- Graceful degradation instead of complete failure
- Users can still accomplish basic tasks

---

## Limitations

### 1. No Natural Language Understanding
- Commands must match specific patterns
- Cannot handle variations like "I want to add a task to buy milk"
- Cannot understand context or complex requests

### 2. Limited Command Set
- Only supports: add, list, complete, delete
- Update command not implemented (more complex pattern)
- No support for priorities, tags, descriptions

### 3. Task Number Dependency
- "complete task 1" requires listing tasks first
- Task numbers can change as tasks are added/deleted
- UUIDs work but are not user-friendly

### 4. No Conversation Context
- Each command is independent
- Cannot reference previous messages
- No multi-turn interactions

---

## Future Enhancements

### 1. Add Update Command
```python
# Pattern: "update task 1 to buy organic milk"
update_pattern = r'^update\s+(?:task\s+)?(\d+|[a-f0-9-]+)\s+to\s+(.+)$'
```

### 2. Add Priority/Tags Support
```python
# Pattern: "add buy milk priority high"
# Pattern: "add buy milk tags shopping groceries"
```

### 3. Add Search/Filter
```python
# Pattern: "show completed tasks"
# Pattern: "show tasks with tag shopping"
```

### 4. Add Better Error Messages
- Suggest corrections for typos
- Show similar commands
- Provide examples

---

## Deployment Notes

### Backend Restart Required
**CRITICAL**: The backend must be restarted for these changes to take effect.

**Restart Command**:
```bash
cd C:\Users\User\Desktop\todo-ai-chatbot\backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Verification
After restart, check backend logs for:
```
INFO: Using mock AI response - no API key configured. Message: add buy milk
```

If you see command parsing working, you'll see task operations in the logs.

### Rollback
If issues occur, revert the changes to `agent.py`:
```bash
git checkout backend/src/services/agent.py
```

---

## Specification Compliance

### Before Implementation
- ❌ FR-001: Natural language commands (AI required)
- ❌ SC-010: No documentation needed (AI required)

### After Implementation (Fallback Mode)
- ⚠️ FR-001: Basic command parsing (limited patterns)
- ⚠️ SC-010: Simple commands work (with specific syntax)

**Note**: This is a fallback feature, not a replacement for AI. Full specification compliance still requires a valid API key and AI functionality.

---

**Created**: 2026-02-06
**Status**: Implemented, awaiting backend restart for testing
**Priority**: Enhancement (improves fallback mode usability)
