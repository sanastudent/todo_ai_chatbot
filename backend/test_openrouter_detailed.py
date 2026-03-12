#!/usr/bin/env python3
"""
Test script to verify OpenRouter configuration is working properly with proper authentication
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_openrouter_raw_http():
    """Test OpenRouter API using raw HTTP requests"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    print("Testing OpenRouter Configuration with Raw HTTP...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key available: {bool(api_key)}")

    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set in environment")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:8000"),
        "X-Title": os.getenv("X_TITLE", "Todo AI Chatbot"),
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, are you working?"}
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }

    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            print(f"Response Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("SUCCESS: Raw HTTP request to OpenRouter succeeded!")
                print(f"Response: {result['choices'][0]['message']['content'][:100]}...")
                return True
            else:
                print(f"ERROR: HTTP request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"ERROR in raw HTTP request: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False


async def test_openrouter_sdk():
    """Test OpenRouter API using OpenAI SDK with proper configuration"""
    from openai import AsyncOpenAI

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    print("\nTesting OpenRouter Configuration with OpenAI SDK...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key available: {bool(api_key)}")

    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set in environment")
        return False

    try:
        # Create client with OpenRouter configuration
        http_client = httpx.AsyncClient(
            timeout=30.0,
            trust_env=False
        )

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )

        # Test with a simple request
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            temperature=0.1,
            max_tokens=50
        )

        print("SUCCESS: OpenAI SDK request to OpenRouter succeeded!")
        print(f"Response: {response.choices[0].message.content[:100]}...")

        await http_client.aclose()
        return True

    except Exception as e:
        print(f"ERROR with OpenAI SDK: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False


async def main():
    print("Testing OpenRouter API Connection Methods...\n")

    # Test with raw HTTP request
    http_success = await test_openrouter_raw_http()

    # Test with OpenAI SDK
    sdk_success = await test_openrouter_sdk()

    print(f"\nResults:")
    print(f"- Raw HTTP Request: {'✅ SUCCESS' if http_success else '❌ FAILED'}")
    print(f"- OpenAI SDK: {'✅ SUCCESS' if sdk_success else '❌ FAILED'}")

    if http_success or sdk_success:
        print("\n🎉 At least one OpenRouter connection method is working!")
        return True
    else:
        print("\n💥 Both OpenRouter connection methods failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\nOpenRouter configuration has at least one working method!")
    else:
        print("\nOpenRouter configuration needs fixing!")