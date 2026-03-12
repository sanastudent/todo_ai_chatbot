import asyncio
import requests
import subprocess
import time
import signal
import os

def test_backend_startup():
    """Test if backend starts correctly and health endpoint works"""

    print("Starting backend server in background...")

    # Start the backend server as a subprocess
    proc = subprocess.Popen([
        'python', 'run_server.py'
    ], cwd=os.path.dirname(__file__))

    try:
        # Wait a bit for server to start
        print("Waiting for server to start...")
        time.sleep(5)

        # Test the health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://localhost:8000/health', timeout=10)

        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check successful: {health_data}")
            return True
        else:
            print(f"❌ Health check failed: Status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"❌ Error during health check: {e}")
        return False
    finally:
        # Terminate the subprocess
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    success = test_backend_startup()
    if success:
        print("\n🎉 Backend startup and health check test PASSED!")
    else:
        print("\n💥 Backend startup test FAILED!")