"""
Test health check through both paths
"""
import httpx
import asyncio

async def test_health_checks():
    print("=" * 60)
    print("HEALTH CHECK TESTS")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test 1: Direct backend health check
        print("\n1. Direct backend health (port 8001):")
        try:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")

        # Test 2: Health check through /api/health (proxy rewrite)
        print("\n2. Through proxy /api/health (port 5174):")
        try:
            response = await client.get("http://localhost:5174/api/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")

        # Test 3: Direct /health through proxy (no /api prefix)
        print("\n3. Direct /health through proxy (port 5174):")
        try:
            response = await client.get("http://localhost:5174/health", timeout=5.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("If test 2 fails but test 1 works, the proxy rewrite is broken.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_health_checks())
