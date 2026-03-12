#!/usr/bin/env python3
"""
Test script to verify the correct OpenRouter configuration using OpenAI SDK
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

async def test_openrouter_proper_config():
    """Test OpenRouter API using OpenAI SDK with the exact configuration needed for OpenRouter"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    print("Testing OpenRouter Configuration with OpenAI SDK...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key available: {bool(api_key)}")

    if not api_key or api_key == "fake-key-for-testing":
        print("WARNING: Using fake API key - will fail with real request")
        print("For real testing, please use a valid OpenRouter API key")
        return False

    try:
        # Create the HTTP client with proper configuration for OpenRouter
        http_client = httpx.AsyncClient(
            timeout=30.0,
            trust_env=False  # Important: prevent proxy interference
        )

        # Create OpenAI client with OpenRouter configuration
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            # Additional headers required by OpenRouter
            default_headers={
                "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:8000"),
                "X-Title": os.getenv("X_TITLE", "Todo AI Chatbot"),
            },
            http_client=http_client
        )

        # Make a test request
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for testing API connectivity."},
                {"role": "user", "content": "Hello, this is a test to verify API connectivity."}
            ],
            temperature=0.1,
            max_tokens=60
        )

        print("✅ SUCCESS: OpenAI SDK request to OpenRouter succeeded!")
        print(f"Response: {response.choices[0].message.content}")

        # Close the HTTP client to prevent resource leaks
        await http_client.aclose()
        return True

    except Exception as e:
        print(f"❌ ERROR with OpenAI SDK: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

        # Attempt to close client if still available
        try:
            await http_client.aclose()
        except:
            pass

        return False

async def main():
    print("Testing OpenRouter API with proper OpenAI SDK configuration...\n")

    success = await test_openrouter_proper_config()

    if success:
        print("\n🎉 OpenRouter configuration is working correctly!")
        print("The AI agent should now be able to connect successfully.")
    else:
        print("\n💥 OpenRouter configuration needs fixing.")
        print("Please ensure you have a valid OpenRouter API key with sufficient credits.")

if __name__ == "__main__":
    asyncio.run(main())