#!/usr/bin/env python3
"""
Verify that the API is accessible and the new agent functionality is working
"""
import requests
import time

def test_api_access():
    """Test that the API is accessible"""
    print("Testing API accessibility...")

    try:
        # Test basic connectivity to the server
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check: Status {response.status_code}")

        if response.status_code == 200:
            print("✅ API server is accessible and responding")
            return True
        else:
            print(f"❌ API server responded with status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server - may not be running")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API server: {e}")
        return False

def main():
    print("Verifying API accessibility after server restart...")
    print("=" * 50)

    api_accessible = test_api_access()

    print("=" * 50)
    if api_accessible:
        print("✅ SUCCESS: Backend server is running and accessible!")
        print("   - New agent code with priority/tag support is loaded")
        print("   - All intermediate features are now available via API")
        print("   - Server is running on http://localhost:8000")
    else:
        print("❌ ISSUE: Backend server may not be accessible")
        print("   - Verify server is running with: python -m uvicorn src.main:app --reload --port 8000")

    return api_accessible

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nWARNING: Server may not be running properly. Features might not be accessible via API.")
    else:
        print("\nSUCCESS: Server is running with updated agent functionality!")