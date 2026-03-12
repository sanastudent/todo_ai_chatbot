#!/usr/bin/env python3
"""
Test script to verify OpenRouter configuration is working properly
"""
import asyncio
import os
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_openrouter_config():
    """Test OpenRouter API configuration"""

    # Load environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    print("Testing OpenRouter Configuration...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key available: {bool(api_key)}")

    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set in environment")
        return False

    # Test API connectivity
    try:
        # Create client with OpenRouter configuration
        http_client = httpx.AsyncClient(
            timeout=30.0,
            trust_env=False
        )

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:8000"),
                "X-Title": os.getenv("X_TITLE", "Todo AI Chatbot"),
            },
            http_client=http_client
        )

        # Test with a simple request
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            temperature=0.1,
            max_tokens=50
        )

        print("SUCCESS: Successfully connected to OpenRouter!")
        print(f"Response: {response.choices[0].message.content[:100]}...")

        await http_client.aclose()
        return True

    except Exception as e:
        print(f"ERROR connecting to OpenRouter: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter_config())
    if success:
        print("\nOpenRouter configuration is working correctly!")
    else:
        print("\nOpenRouter configuration needs fixing!")