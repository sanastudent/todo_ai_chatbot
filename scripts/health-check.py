#!/usr/bin/env python3
"""
Health check script to verify the backend is running before launching the frontend.
"""

import sys
import time
import subprocess
import requests
import os
import threading
import signal
import math

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"
MAX_RETRIES = 30
INITIAL_RETRY_INTERVAL = 2  # seconds
TIMEOUT_PER_CHECK = 5  # seconds

def check_health():
    """Check if the backend health endpoint is responding."""
    retry_count = 0
    current_interval = INITIAL_RETRY_INTERVAL

    while retry_count < MAX_RETRIES:
        try:
            print(f"[INFO] Attempting health check ({retry_count + 1}/{MAX_RETRIES})...")

            response = requests.get(HEALTH_ENDPOINT, timeout=TIMEOUT_PER_CHECK)

            if response.status_code == 200:
                print("[SUCCESS] Backend health check passed!")
                print(f"[INFO] Response: {response.json()}")
                return True
            elif response.status_code == 404:
                print(f"[ERROR] Health endpoint not found: {HEALTH_ENDPOINT}")
            else:
                print(f"[ERROR] Backend health check failed with status: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"[WARN] Backend not reachable yet: Connection refused")
        except requests.exceptions.Timeout:
            print(f"[WARN] Backend health check timed out after {TIMEOUT_PER_CHECK}s")
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Request error during health check: {str(e)}")
        except Exception as e:
            print(f"[WARN] Unexpected error during health check: {str(e)}")

        retry_count += 1
        if retry_count < MAX_RETRIES:
            # Exponential backoff with a maximum cap
            current_interval = min(current_interval * 1.1, 10)  # Cap at 10 seconds
            print(f"[INFO] Waiting {current_interval:.1f}s before retry {retry_count + 1}/{MAX_RETRIES}...")
            time.sleep(current_interval)

    print("[ERROR] Backend health check failed after maximum retries")
    return False

def main():
    """Main function to check backend health and execute command if healthy."""
    print("[INFO] Starting health check process...")
    print(f"[INFO] Health endpoint: {HEALTH_ENDPOINT}")
    print(f"[INFO] Maximum retries: {MAX_RETRIES}")
    print(f"[INFO] Initial retry interval: {INITIAL_RETRY_INTERVAL}s")
    print(f"[INFO] Timeout per check: {TIMEOUT_PER_CHECK}s")

    # Check if the health endpoint is available
    if check_health():
        print("[SUCCESS] Backend is healthy and ready!")

        # Execute the original command that was passed to this script
        if len(sys.argv) > 1:
            command = sys.argv[1:]
            print(f"[INFO] Executing command: {' '.join(command)}")

            try:
                # Execute the command and wait for it to complete
                result = subprocess.run(command, check=True)
                print(f"[INFO] Command completed successfully with return code: {result.returncode}")
                sys.exit(result.returncode)
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Command failed with return code: {e.returncode}")
                sys.exit(e.returncode)
            except KeyboardInterrupt:
                print("[INFO] Command interrupted by user")
                sys.exit(130)  # Standard exit code for SIGINT
        else:
            print("[INFO] Backend is healthy, no command to execute")
            return 0
    else:
        print("[ERROR] Backend health check failed, cannot proceed.")
        print("[ERROR] Exiting with code 1")
        sys.exit(1)

if __name__ == "__main__":
    main()