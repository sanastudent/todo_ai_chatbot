#!/usr/bin/env python3
"""
Test script to verify the fixed OpenRouter authentication
"""
import os
import asyncio
from openai import AsyncOpenAI
import httpx
import logging
from dotenv import load_dotenv

# Set up logging to see debug information
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

async def test_fixed_authentication():
    """Test the fixed OpenRouter authentication"""

    print("=== Testing Fixed OpenRouter Authentication ===\n")

    # Get configuration
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    print(f"Configuration:")
    print(f"  API Key available: {'Yes' if api_key else 'No'}")
    print(f"  API Key format check: {api_key.startswith('sk-or-') if api_key else 'N/A'}")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print()

    if not api_key:
        print("ERROR: No API key found!")
        return False

    # Test the new configuration approach
    print("Testing new configuration approach...")

    # Prepare additional headers
    additional_headers = {}
    if os.getenv("HTTP_REFERER"):
        additional_headers["HTTP-Referer"] = os.getenv("HTTP_REFERER")
        print(f"  Added HTTP-Referer: {os.getenv('HTTP_REFERER')}")
    if os.getenv("X_TITLE"):
        additional_headers["X-Title"] = os.getenv("X_TITLE")
        print(f"  Added X-Title: {os.getenv('X_TITLE')}")

    try:
        # Create HTTP client
        http_client = httpx.AsyncClient(
            timeout=30.0,
            trust_env=False
        )

        # Create the client with the fixed configuration
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=additional_headers,
            http_client=http_client
        )

        print("  ✅ AsyncOpenAI client created successfully")

        # Make a test call
        print("  Making test API call...")
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you working now?"}],
            max_tokens=20
        )

        print(f"  ✅ API call succeeded! Response: {response.choices[0].message.content[:50]}...")

        await http_client.aclose()
        return True

    except Exception as e:
        print(f"  ❌ API call failed: {e}")

        # Check for the specific error we're trying to fix
        error_msg = str(e).lower()
        if 'cookie auth' in error_msg:
            print("  💡 Still getting the 'cookie auth' error - need further investigation")

        try:
            await http_client.aclose()
        except:
            pass

        return False

async def test_raw_request():
    """Test with raw HTTP request to compare"""
    print("\n=== Testing Raw HTTP Request ===")

    import json

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Add OpenRouter-specific headers if available
    if os.getenv("HTTP_REFERER"):
        headers["HTTP-Referer"] = os.getenv("HTTP_REFERER")
    if os.getenv("X_TITLE"):
        headers["X-Title"] = os.getenv("X_TITLE")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Test message"}],
        "max_tokens": 10
    }

    print(f"Headers being sent: {list(headers.keys())}")

    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            print(f"Raw request status: {response.status_code}")
            if response.status_code != 200:
                print(f"Raw request error: {response.text}")

                if 'cookie auth' in response.text.lower():
                    print("  💡 Raw request also shows 'cookie auth' error")

                return False
            else:
                print("  ✅ Raw request succeeded!")
                return True

    except Exception as e:
        print(f"Raw request failed: {e}")
        return False

async def main():
    print("Testing OpenRouter authentication fixes...\n")

    # Test the fixed authentication
    sdk_result = await test_fixed_authentication()

    # Test raw request for comparison
    raw_result = await test_raw_request()

    print(f"\n=== Results ===")
    print(f"SDK Test: {'✅ PASS' if sdk_result else '❌ FAIL'}")
    print(f"Raw Request: {'✅ PASS' if raw_result else '❌ FAIL'}")

    if sdk_result or raw_result:
        print("\n✅ At least one test passed - authentication might be working")
        print("   (Note: Using fake key will always fail, but configuration may be correct)")
    else:
        print("\n❌ Both tests failed - authentication still has issues")

    print(f"\nThe most important factor is having a valid API key.")
    print(f"The current key format is: {'Valid' if api_key and api_key.startswith('sk-or-') else 'Invalid/Fake'}")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))  # Ensure we're in the backend directory
    asyncio.run(main())