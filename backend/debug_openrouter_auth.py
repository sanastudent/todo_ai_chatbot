#!/usr/bin/env python3
"""
Debug script to identify the exact OpenRouter authentication issue
"""
import os
import asyncio
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def debug_openrouter_connection():
    """Debug OpenRouter connection by examining each step"""

    print("=== OpenRouter Authentication Debug ===\n")

    # Step 1: Check environment variables
    print("1. Environment Variables:")
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    http_referer = os.getenv("HTTP_REFERER", "http://localhost:8000")
    x_title = os.getenv("X_TITLE", "Todo AI Chatbot")

    print(f"   OPENROUTER_API_KEY: {'SET' if api_key else 'NOT SET'}")
    print(f"   API Key value: {api_key[:10] + '...' if api_key and len(api_key) > 10 else 'None'}")
    print(f"   OPENROUTER_BASE_URL: {base_url}")
    print(f"   OPENROUTER_MODEL: {model}")
    print(f"   HTTP_REFERER: {http_referer}")
    print(f"   X_TITLE: {x_title}\n")

    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY is not set!")
        return False

    # Step 2: Test HTTP client creation
    print("2. Creating HTTP client...")
    http_client = httpx.AsyncClient(
        timeout=30.0,
        trust_env=False
    )
    print("   HTTP client created successfully\n")

    # Step 3: Test AsyncOpenAI client creation with different configurations
    print("3. Testing different AsyncOpenAI client configurations:")

    # Configuration 1: Basic setup
    print("   Config 1 - Basic setup:")
    try:
        client1 = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        print("     ✅ Client created successfully")

        # Try a basic test call
        print("     Attempting basic API call...")
        response1 = await client1.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        print("     ✅ Basic API call successful!")

    except Exception as e:
        print(f"     ❌ Basic config failed: {e}")

    print()

    # Configuration 2: With default headers
    print("   Config 2 - With default headers:")
    try:
        client2 = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": http_referer,
                "X-Title": x_title,
            },
            http_client=http_client
        )
        print("     ✅ Client with headers created successfully")

        # Try a test call
        print("     Attempting API call with headers...")
        response2 = await client2.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Test with headers"}],
            max_tokens=10
        )
        print("     ✅ API call with headers successful!")

    except Exception as e:
        print(f"     ❌ Config with headers failed: {e}")
        error_msg = str(e).lower()
        if 'cookie auth' in error_msg:
            print("     💡 This is the 'cookie auth' error we're seeing!")

    print()

    # Configuration 3: Using raw HTTP request to see the actual request
    print("   Config 3 - Raw HTTP request to understand the issue:")
    import json

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": http_referer,
        "X-Title": x_title,
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Simple test"}],
        "max_tokens": 10
    }

    print(f"     Headers to be sent: {headers}")
    print(f"     Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as temp_client:
            response = await temp_client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            print(f"     Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"     Response text: {response.text}")

                if 'cookie auth' in response.text.lower():
                    print("     💡 The raw HTTP request also shows the cookie auth error!")
            else:
                print("     ✅ Raw HTTP request succeeded!")

    except Exception as e:
        print(f"     ❌ Raw HTTP request failed: {e}")

    # Close HTTP client
    await http_client.aclose()

    print("\n=== Debug Complete ===")
    return True

if __name__ == "__main__":
    asyncio.run(debug_openrouter_connection())