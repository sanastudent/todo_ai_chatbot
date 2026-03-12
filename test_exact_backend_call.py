"""
CRITICAL TEST: Simulate exact backend API call with tools
This tests the EXACT call the backend makes, including function calling
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx
from openai import AsyncOpenAI
import json

# Load environment
load_dotenv()

def get_mcp_tool_schemas():
    """Same tool schemas as backend"""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["user_id", "title"]
                }
            }
        }
    ]

async def test_exact_backend_call():
    """Test the EXACT API call the backend makes"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

    print("=" * 70)
    print("EXACT BACKEND API CALL TEST (WITH TOOLS)")
    print("=" * 70)
    print()
    print(f"API Key: {api_key[:20]}..." if api_key else "NOT SET")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print()

    # Test message
    test_message = "add buy fresh flowers"

    print(f"Test Message: '{test_message}'")
    print()

    # Create HTTP client exactly like backend
    http_client = httpx.AsyncClient(
        timeout=30.0,
        trust_env=False
    )

    try:
        # Prepare headers exactly like backend
        additional_headers = {}
        if os.getenv("HTTP_REFERER"):
            additional_headers["HTTP-Referer"] = os.getenv("HTTP_REFERER")
        if os.getenv("X_TITLE"):
            additional_headers["X-Title"] = os.getenv("X_TITLE")

        print(f"Additional Headers: {additional_headers}")
        print()

        # Create client exactly like backend
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=additional_headers,
            http_client=http_client
        )

        # Prepare messages exactly like backend
        system_prompt = """You are an AI assistant for a task management application. Help users manage their tasks by understanding their natural language requests and using the appropriate tools.
        - Use add_task to create new tasks when users want to add, remember, or create something
        - Use list_tasks to show users their tasks when they ask to see, show, list, or view tasks
        - Use complete_task to mark tasks as done when users say they finished, completed, or are done with something
        - Use update_task to modify existing tasks when users want to change details
        - Use delete_task to remove tasks when users want to eliminate them

        IMPORTANT: When users refer to tasks by number (e.g., "complete task 1", "delete task 3", "update task 2"), use that number as the task_id. The system will automatically map the number to the actual task ID based on the most recent task list.

        CRITICAL: When a tool returns a message asking for confirmation or additional information (containing words like "confirm", "sure", "provide", "respond with"), you MUST relay that message to the user EXACTLY as provided by the tool. Do NOT say the operation completed - instead, ask the user for the required information or confirmation.

        Be helpful and conversational in your responses."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_message}
        ]

        print("Making API call with tools (function calling)...")
        print()

        # Make the EXACT call the backend makes
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=get_mcp_tool_schemas(),
            tool_choice="auto",
            max_tokens=2048
        )

        print("[SUCCESS] API call with tools succeeded!")
        print()

        # Check response
        response_message = response.choices[0].message
        print(f"Response content: {response_message.content}")
        print(f"Tool calls: {response_message.tool_calls}")

        if response_message.tool_calls:
            print()
            print("Tool calls detected:")
            for tc in response_message.tool_calls:
                print(f"  Function: {tc.function.name}")
                print(f"  Arguments: {tc.function.arguments}")

        await http_client.aclose()
        return True

    except Exception as e:
        print(f"[FAIL] API call failed!")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print()

        # Get detailed error info
        if hasattr(e, '__dict__'):
            print("Error details:")
            for key, value in e.__dict__.items():
                print(f"  {key}: {value}")

        try:
            await http_client.aclose()
        except:
            pass

        return False

async def main():
    """Run test"""

    # Change to backend directory
    import sys
    sys.path.insert(0, 'C:/Users/User/Desktop/todo-ai-chatbot/backend')
    os.chdir('C:/Users/User/Desktop/todo-ai-chatbot/backend')

    # Reload environment
    load_dotenv(override=True)

    success = await test_exact_backend_call()

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if success:
        print("[SUCCESS] The exact backend API call works!")
        print()
        print("This means:")
        print("1. OpenRouter API is working")
        print("2. Function calling (tools) is working")
        print("3. The model supports tools")
        print()
        print("The issue must be:")
        print("- An exception is being caught and suppressed")
        print("- The backend is not actually reaching this code")
        print("- There's a different code path being executed")
    else:
        print("[FAILURE] The exact backend API call fails!")
        print()
        print("This explains the error message.")
        print("The backend tries to call OpenRouter with tools,")
        print("it fails, and falls back to mock_ai_response().")
        print()
        print("Possible causes:")
        print("1. Model doesn't support function calling")
        print("2. Tool schema format is incorrect")
        print("3. OpenRouter API issue with this specific model")

if __name__ == "__main__":
    asyncio.run(main())
