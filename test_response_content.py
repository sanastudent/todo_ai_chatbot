"""
Test to capture the actual response from both paths
"""
import httpx
import json
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

async def test_response():
    import asyncio

    print("Testing backend response...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test direct backend
        response = await client.post(
            "http://localhost:8001/api/user-test/chat",
            json={"message": "add buy fresh flowers"},
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()

        data = response.json()
        print("Response JSON structure:")
        print(f"  Keys: {list(data.keys())}")
        print()

        if 'response' in data:
            response_text = data['response']
            print(f"Response field content:")
            print(f"  Length: {len(response_text)} characters")
            print(f"  First 100 chars: {response_text[:100]}")

            # Check for key phrases
            couldnt_understand = "couldn't understand" in response_text.lower()
            task_added = "Task added" in response_text
            ai_not_available = "AI not available" in response_text

            print(f"  Contains 'couldn't understand': {couldnt_understand}")
            print(f"  Contains 'Task added': {task_added}")
            print(f"  Contains 'AI not available': {ai_not_available}")

        print()
        print("Full response (ASCII-safe):")
        print(json.dumps(data, indent=2, ensure_ascii=True))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_response())
