# OpenRouter API Setup Guide

## Overview

This Todo AI Chatbot requires a valid OpenRouter API key to enable AI-powered natural language processing. Without a valid API key, the system operates in fallback mode with limited functionality.

## Why OpenRouter is Required

The application's core functionality depends on AI natural language processing:

- **FR-001**: System MUST interpret natural language commands (e.g., "Add task to buy groceries")
- **FR-006**: AI agent MUST parse user intent and select appropriate MCP tools
- **FR-007**: AI agent MUST provide conversational, user-friendly responses
- **SC-003**: System must correctly interpret 90% of common task management commands
- **SC-010**: New users can successfully add their first task without documentation

**Without a valid API key**, the system cannot meet these specification requirements and will display:
> "⚠️ Note: AI natural language processing is not available (no API key configured)."

## Getting Your OpenRouter API Key

### Step 1: Sign Up for OpenRouter

1. Visit [https://openrouter.ai](https://openrouter.ai)
2. Click "Sign Up" or "Get Started"
3. Create an account using your email or GitHub
4. Verify your email address

### Step 2: Add Credits

OpenRouter operates on a pay-as-you-go model:

1. Navigate to your account dashboard
2. Click "Credits" or "Billing"
3. Add credits to your account (minimum $5 recommended)
4. Credits are used per API request based on the model

### Step 3: Generate API Key

1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Click "Create Key" or "Generate New Key"
3. Give your key a descriptive name (e.g., "Todo Chatbot Dev")
4. Copy the generated API key (format: `sk-or-v1-...`)
5. **IMPORTANT**: Save this key securely - you won't be able to see it again

## Configuring Your Application

### Step 1: Locate the .env File

The `.env` file is located at:
```
C:\Users\User\Desktop\todo-ai-chatbot\backend\.env
```

### Step 2: Update the API Key

Open the `.env` file and update the `OPENROUTER_API_KEY` value:

```bash
# Before (fake key - AI disabled)
OPENROUTER_API_KEY=fake-key-for-testing

# After (real key - AI enabled)
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### Step 3: Verify Other Settings

Ensure these settings are also configured:

```bash
OPENROUTER_MODEL=google/gemini-pro
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
HTTP_REFERER=http://localhost:8000
X_TITLE=Todo AI Chatbot
```

### Step 4: Restart the Backend

After updating the `.env` file, restart your backend server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Verifying Your Configuration

### Method 1: Check Backend Logs

When the backend starts, you should see:
```
INFO: Using valid OpenRouter API key for requests
```

If you see this instead, your key is invalid:
```
WARNING: Fake API key detected, using mock response for testing
```

### Method 2: Test with a Chat Request

Send a test request to the API:

```bash
curl -X POST http://localhost:8000/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy milk"}'
```

**Expected Response (AI enabled):**
```json
{
  "response": "I've added 'buy milk' to your tasks. Is there anything else you'd like me to help with?",
  "conversation_id": "...",
  "message_id": "..."
}
```

**Fallback Response (AI disabled):**
```json
{
  "response": "⚠️ Note: AI natural language processing is not available (no API key configured).\n\nTry using specific commands like:\n• 'add [task]' - Add a new task\n...",
  "conversation_id": "...",
  "message_id": "..."
}
```

### Method 3: Use the Frontend

1. Open the frontend at `http://localhost:5174`
2. Type: "Add task to buy groceries"
3. If AI is enabled, you'll get a conversational response
4. If AI is disabled, you'll see the "not available" message

## Troubleshooting

### Issue: "AI natural language processing is not available"

**Cause**: Invalid or missing API key

**Solutions**:
1. Verify your API key starts with `sk-or-v1-`
2. Check for typos when copying the key
3. Ensure no extra spaces before/after the key in `.env`
4. Restart the backend server after updating `.env`

### Issue: "Authentication error" or "401 Unauthorized"

**Cause**: Invalid API key or insufficient credits

**Solutions**:
1. Verify your API key is still valid at [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Check your credit balance at [https://openrouter.ai/credits](https://openrouter.ai/credits)
3. Generate a new API key if the old one was revoked
4. Add more credits to your account

### Issue: "429 Rate Limit" errors

**Cause**: Too many requests in a short time

**Solutions**:
1. Wait a few seconds before retrying
2. The system has built-in retry logic with exponential backoff
3. Consider upgrading your OpenRouter plan for higher rate limits

### Issue: Backend logs show "Fake API key detected"

**Cause**: The `.env` file still contains `fake-key-for-testing`

**Solutions**:
1. Open `backend/.env` (not `.env.example`)
2. Replace the fake key with your real OpenRouter API key
3. Restart the backend server

## Security Best Practices

### DO:
- ✅ Keep your API key in the `.env` file (already in `.gitignore`)
- ✅ Use different API keys for development and production
- ✅ Rotate your API keys periodically
- ✅ Monitor your usage on the OpenRouter dashboard
- ✅ Set spending limits on your OpenRouter account

### DON'T:
- ❌ Commit your `.env` file to version control
- ❌ Share your API key in screenshots or logs
- ❌ Use the same API key across multiple projects
- ❌ Store API keys in frontend code
- ❌ Put real API keys in `.env.example` files

## Cost Management

### Understanding Costs

OpenRouter charges per token (input + output):
- **Gemini Pro**: ~$0.000125 per 1K input tokens, ~$0.000375 per 1K output tokens
- Average chat request: ~500 tokens = ~$0.0003 per request
- $5 credit ≈ 16,000+ chat requests

### Monitoring Usage

1. Visit [https://openrouter.ai/activity](https://openrouter.ai/activity)
2. View your request history and costs
3. Set up spending alerts
4. Track usage by API key

### Reducing Costs

1. Use more efficient models (e.g., `google/gemini-flash` instead of `google/gemini-pro`)
2. Implement request caching for repeated queries
3. Set conversation history limits
4. Use shorter system prompts

## Alternative AI Providers

If you prefer not to use OpenRouter, you can modify the code to use:

### OpenAI Direct
```bash
OPENAI_API_KEY=sk-proj-your-openai-key
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic Claude
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

**Note**: Code modifications required for alternative providers. OpenRouter is recommended as it provides access to multiple models through a single API.

## Specification Compliance

With a valid OpenRouter API key configured, the system meets all specification requirements:

- ✅ **FR-001**: Natural language command interpretation enabled
- ✅ **FR-006**: AI agent parses user intent and calls MCP tools
- ✅ **FR-007**: Conversational, user-friendly responses provided
- ✅ **SC-003**: 90%+ command interpretation accuracy (Gemini Pro)
- ✅ **SC-010**: No documentation needed for first task

Without a valid API key, the system operates in **fallback mode** and cannot meet these requirements.

## Support

### OpenRouter Support
- Documentation: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- Discord: [https://discord.gg/openrouter](https://discord.gg/openrouter)
- Email: support@openrouter.ai

### Application Support
- Check backend logs for detailed error messages
- Review the README.md for general setup instructions
- Ensure all environment variables are configured correctly

## Quick Reference

### Valid API Key Format
```
sk-or-v1-[64 hexadecimal characters]
```

### Minimum Configuration
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=google/gemini-pro
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Verification Command
```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Valid' if os.getenv('OPENROUTER_API_KEY', '').startswith('sk-or-v1-') else 'Invalid')"
```

### Restart Backend
```bash
# Windows
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the startup script
start_todo_app.ps1
```

---

**Last Updated**: 2026-02-06
**Version**: 1.0
