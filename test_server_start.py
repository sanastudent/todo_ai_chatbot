#!/usr/bin/env python3
"""
Test to see if we can start the server and handle a simple request
"""
import os
import sys
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend/src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.main import app
from fastapi.testclient import TestClient


def test_server_health():
    """Test the health endpoint to make sure the server can start"""
    print("Testing server health endpoint...")

    client = TestClient(app)

    try:
        response = client.get("/health")
        print(f"Health check response: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")

    except Exception as e:
        print(f"✗ Error during health check: {e}")


def test_chat_endpoint():
    """Test the chat endpoint with a simple request that caused HTTP 500"""
    print("\nTesting chat endpoint with 'add groceries'...")

    client = TestClient(app)

    try:
        # Test with a simple request that was causing issues
        response = client.post(
            "/api/test-user/chat",
            json={"message": "add groceries"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Chat response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response content: {response.text}")
        else:
            print(f"Response: {response.json()}")

        if response.status_code < 500:
            print("✓ Chat endpoint responded without 500 error")
        else:
            print("✗ Chat endpoint returned 500 error")

    except Exception as e:
        print(f"✗ Error during chat request: {e}")
        import traceback
        print(traceback.format_exc())


def test_mock_session():
    """Test with mocked database session to isolate the issue"""
    print("\nTesting with mocked session...")

    # Import the invoke_agent function
    from src.services.agent import invoke_agent
    from src.mcp.tools import add_task

    # Create a mock session
    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Test the invoke_agent function directly with mocked tools
    async def test_invoke():
        try:
            # Patch the add_task function to return a mock result
            with patch('src.services.agent.add_task') as mock_add_task:
                mock_add_task.return_value = {
                    "task_id": "mock-id-123",
                    "title": "groceries",
                    "created_at": "2026-01-12T10:00:00Z",
                    "was_duplicate": False
                }

                result = await invoke_agent(
                    user_id="test-user",
                    conversation_id="conv-123",
                    user_message="add groceries",
                    db_session=mock_session
                )
                print(f"invoke_agent result: {result}")
                return True

        except Exception as e:
            print(f"Error in invoke_agent: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    # Run the async test
    result = asyncio.run(test_invoke())
    if result:
        print("✓ invoke_agent worked with mocked tools")
    else:
        print("✗ invoke_agent failed with mocked tools")


if __name__ == "__main__":
    print("Starting server test...")
    test_server_health()
    test_chat_endpoint()
    test_mock_session()
    print("\nServer tests completed.")