"""
CRITICAL DIAGNOSTIC: Test actual OpenRouter API call
This will reveal why the API call is failing and falling back to mock response
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx
from openai import AsyncOpenAI

# Load environment
load_dotenv()

async def test_openrouter_api():
    """Test the actual OpenRouter API call that the backend makes"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

    print("=" * 70)
    print("OPENROUTER API DIAGNOSTIC TEST")
    print("=" * 70)
    print()
    print(f"API Key: {api_key[:20]}..." if api_key else "NOT SET")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print()

    if not api_key:
        print("[FAIL] No API key found")
        return False

    if not api_key.startswith("sk-or-"):
        print(f"[WARN] API key format unexpected: {api_key[:10]}...")

    # Test 1: Direct HTTP request to OpenRouter
    print("TEST 1: Direct HTTP Request to OpenRouter")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:5174"),
                    "X-Title": os.getenv("X_TITLE", "Todo AI Chatbot")
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say 'test successful' if you can read this."}
                    ],
                    "max_tokens": 50
                }
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"[PASS] OpenRouter API works!")
                print(f"Response: {content}")
                return True
            else:
                print(f"[FAIL] OpenRouter returned error")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"[FAIL] Request failed: {e}")
            return False

    print()

    # Test 2: Using OpenAI client (like backend does)
    print("TEST 2: Using OpenAI Client (Backend Method)")
    print("-" * 70)

    try:
        http_client = httpx.AsyncClient(timeout=30.0, trust_env=False)

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:5174"),
                "X-Title": os.getenv("X_TITLE", "Todo AI Chatbot")
            },
            http_client=http_client
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'test successful' if you can read this."}
            ],
            max_tokens=50
        )

        content = response.choices[0].message.content
        print(f"[PASS] OpenAI client works!")
        print(f"Response: {content}")

        await http_client.aclose()
        return True

    except Exception as e:
        print(f"[FAIL] OpenAI client failed: {e}")
        print(f"Error type: {type(e).__name__}")

        # Try to get more details
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")

        try:
            await http_client.aclose()
        except:
            pass

        return False

async def main():
    """Run diagnostic tests"""

    # Change to backend directory to load .env
    import sys
    sys.path.insert(0, 'C:/Users/User/Desktop/todo-ai-chatbot/backend')
    os.chdir('C:/Users/User/Desktop/todo-ai-chatbot/backend')

    # Reload environment from backend directory
    load_dotenv(override=True)

    success = await test_openrouter_api()

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if success:
        print("[SUCCESS] OpenRouter API is working correctly")
        print()
        print("This means the issue is NOT with OpenRouter authentication.")
        print("The backend should be able to call OpenRouter successfully.")
        print()
        print("Next steps:")
        print("1. Check backend logs when sending message from browser")
        print("2. Look for exceptions in call_openai_agent()")
        print("3. Verify the backend is actually trying to call OpenRouter")
    else:
        print("[FAILURE] OpenRouter API is NOT working")
        print()
        print("This explains why backend falls back to mock_ai_response.")
        print("The error message you see is the fallback when API fails.")
        print()
        print("Possible causes:")
        print("1. Invalid API key")
        print("2. Network connectivity issues")
        print("3. OpenRouter service down")
        print("4. Rate limiting")
        print("5. Incorrect model name")

if __name__ == "__main__":
    asyncio.run(main())
