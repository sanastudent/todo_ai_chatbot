# Todo AI Chatbot - MCP Agent Integration Plan

## Problem Statement
The current system uses primitive regex pattern matching instead of proper AI agent with MCP tools. This causes:
- Only 2 commands to work out of 20+ possible commands
- Fallback to mock AI response for unrecognized patterns
- No actual AI intent recognition or tool calling

## Current Architecture vs Desired Architecture

### Current (Broken)
Client → FastAPI → invoke_agent() → Regex Patterns → MCP Tools (Direct Calls) → Response

### Desired (Proper Implementation)
Client → FastAPI → OpenAI Agent → MCP Tools (Function Calling) → Response

## Implementation Plan

### Phase 1: Install Required Dependencies
- Install OpenAI Python SDK
- Install any additional dependencies for AI agent functionality
- Verify MCP integration is working

### Phase 2: Create AI Agent Integration
- Replace current invoke_agent() with proper OpenAI agent
- Configure the agent with appropriate system message
- Register MCP tools as function definitions for the agent
- Implement proper function calling mechanism

### Phase 3: Update Agent Service
- Modify src/services/agent.py to use OpenAI agent
- Remove regex pattern matching code
- Implement proper tool calling and response handling
- Maintain fallback mechanisms for error handling

### Phase 4: MCP Tools Integration
- Ensure MCP tools are properly exposed as function definitions
- Create proper JSON schemas for each MCP tool
- Map agent function calls to MCP tool calls

### Phase 5: Testing and Validation
- Test all command variations work with AI understanding
- Verify MCP tools are properly called
- Ensure conversation history is maintained
- Validate error handling and fallbacks

## Detailed Implementation Steps

### Step 1: Update Dependencies
```bash
pip install openai
```

### Step 2: Create MCP Tool Schema Generator
Create a function to convert MCP tools into OpenAI-compatible function schemas.

### Step 3: Update invoke_agent Function
Replace current implementation with:
1. Initialize OpenAI client
2. Prepare conversation history
3. Define available functions (MCP tools)
4. Call OpenAI agent with function definitions
5. Process tool calls and responses
6. Return formatted response

### Step 4: Maintain Backward Compatibility
- Keep existing database interfaces
- Preserve conversation persistence
- Maintain error handling patterns

## Key Files to Modify

1. `backend/src/services/agent.py` - Main agent implementation
2. `backend/src/api/routes.py` - Chat endpoint (minimal changes)
3. `backend/src/mcp/server.py` - Ensure tools are accessible as function schemas

## Success Criteria

- All natural language commands work without specific patterns
- AI properly understands intent and calls appropriate tools
- MCP tools are invoked via function calling, not direct calls
- Conversation history is properly maintained
- Error handling remains robust
- System continues to work with existing database and UI