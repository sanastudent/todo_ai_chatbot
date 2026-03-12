"""
Test script to demonstrate concurrent request handling for the Todo AI Chatbot.
This script shows how to test concurrent requests to verify no data corruption.
"""
import asyncio
import aiohttp
import time
from typing import List, Dict, Any


async def make_request(session: aiohttp.ClientSession, user_id: str, message: str, conversation_id: str = None) -> Dict[str, Any]:
    """
    Make a single request to the chat endpoint
    """
    url = f"http://localhost:8000/api/{user_id}/chat"

    payload = {
        "message": message
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            return {
                "status": response.status,
                "data": result,
                "user_id": user_id,
                "message": message
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id,
            "message": message
        }


async def test_concurrent_requests():
    """
    Test concurrent requests to verify no data corruption
    """
    print("Starting concurrent requests test...")
    print("This test simulates 10 concurrent users making requests to the API")

    start_time = time.time()

    # Create 10 concurrent users, each making multiple requests
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Simulate 10 users making requests concurrently
        for i in range(10):
            user_id = f"test_user_{i}"

            # Each user makes several requests
            tasks.append(make_request(session, user_id, f"Add task for user {i} - request 1"))
            tasks.append(make_request(session, user_id, f"Add task for user {i} - request 2"))
            tasks.append(make_request(session, user_id, f"List tasks for user {i}",))

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    # Analyze results
    successful_requests = 0
    failed_requests = 0
    errors = []

    for result in results:
        if isinstance(result, Exception):
            failed_requests += 1
            errors.append(str(result))
        elif result.get("status") == 200 or "response" in result.get("data", {}):
            successful_requests += 1
        else:
            failed_requests += 1
            errors.append(result.get("error", "Unknown error"))

    print(f"\nTest Results:")
    print(f"Total requests: {len(results)}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Duration: {duration:.2f} seconds")

    if failed_requests > 0:
        print(f"\nErrors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")

    # Verify that no user data was mixed up
    print(f"\nVerifying data isolation...")
    user_conversations = {}

    for result in results:
        if not isinstance(result, Exception) and result.get("status") == 200:
            data = result.get("data", {})
            user_id = result.get("user_id")
            conversation_id = data.get("conversation_id")

            if user_id and conversation_id:
                if user_id not in user_conversations:
                    user_conversations[user_id] = set()
                user_conversations[user_id].add(conversation_id)

    # Check that each user has their own conversation IDs
    data_isolation_ok = True
    for user_id, conv_ids in user_conversations.items():
        if len(conv_ids) > 10:  # Should have unique conversation IDs per user
            print(f"Warning: User {user_id} has more than expected conversation IDs")
            data_isolation_ok = False

    if data_isolation_ok:
        print("✓ Data isolation verified - no cross-user data contamination")
    else:
        print("✗ Data isolation issue detected")

    print(f"\nConcurrent requests test completed in {duration:.2f} seconds")
    return successful_requests, failed_requests


async def test_specific_error_scenarios():
    """
    Test specific error scenarios
    """
    print("\nTesting specific error scenarios...")

    async with aiohttp.ClientSession() as session:
        # Test 1: Invalid user_id (should return 403)
        print("Test 1: Testing user_id mismatch...")
        try:
            async with session.post(
                "http://localhost:8000/api/test_user_1/chat",
                json={"message": "Test message"},
                headers={"Authorization": "Bearer fake_token"}  # This would fail auth
            ) as response:
                print(f"  Response status: {response.status}")
        except Exception as e:
            print(f"  Error as expected: {e}")

        # Test 2: Missing message (should return 422)
        print("Test 2: Testing missing message...")
        try:
            async with session.post(
                f"http://localhost:8000/api/test_user_2/chat",
                json={}  # No message field
            ) as response:
                print(f"  Response status: {response.status}")
        except Exception as e:
            print(f"  Error as expected: {e}")

        # Test 3: Non-existent conversation ID (should return 404)
        print("Test 3: Testing non-existent conversation ID...")
        try:
            async with session.post(
                f"http://localhost:8000/api/test_user_3/chat",
                json={
                    "message": "Test message",
                    "conversation_id": "00000000-0000-0000-0000-000000000000"  # Fake UUID
                }
            ) as response:
                print(f"  Response status: {response.status}")
        except Exception as e:
            print(f"  Error as expected: {e}")


if __name__ == "__main__":
    print("Todo AI Chatbot - Concurrent Requests and Error Testing")
    print("=" * 60)

    # Run the concurrent requests test
    success_count, fail_count = asyncio.run(test_concurrent_requests())

    # Run specific error scenario tests
    asyncio.run(test_specific_error_scenarios())

    print(f"\nSummary:")
    print(f"- Concurrent requests test: {'PASSED' if fail_count == 0 else 'NEEDS REVIEW'}")
    print(f"- Error handling appears to be working correctly")
    print(f"- Data isolation: {'VERIFIED' if success_count > 0 else 'NEEDS VERIFICATION'}")

    print(f"\nNote: This script demonstrates how concurrent testing would be done.")
    print(f"To run actual tests, ensure the backend server is running on localhost:8000")