#!/usr/bin/env python3
"""
Test script to validate the health check functionality
"""

import subprocess
import sys
import time
import requests
import os

def test_health_check_script():
    """Test the health check script functionality"""
    print("Testing health check script...")

    # Test with a mock backend that's not running
    try:
        result = subprocess.run([
            sys.executable,
            'scripts/health-check.py',
            'echo', 'test'
        ], timeout=10, capture_output=True, text=True)

        print(f"Health check script exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        if result.returncode != 0:
            print("[PASS] Health check correctly failed when backend not available")
        else:
            print("[FAIL] Health check should have failed when backend not available")

    except subprocess.TimeoutExpired:
        print("[PASS] Health check script timed out as expected when backend not available")
    except Exception as e:
        print(f"Error running health check test: {e}")

def test_port_configuration():
    """Test that port configuration is correct"""
    print("\nTesting port configuration...")

    # Read the vite.config.js file
    with open('frontend/vite.config.js', 'r') as f:
        content = f.read()

    if 'target: \'http://localhost:8000\'' in content:
        print("[PASS] Frontend proxy correctly configured to port 8000")
    else:
        print("[FAIL] Frontend proxy not correctly configured")

    # Check backend port
    with open('backend/run_server.py', 'r') as f:
        backend_content = f.read()

    if 'API_PORT", "8000"' in backend_content:
        print("[PASS] Backend correctly configured to run on port 8000")
    else:
        print("[FAIL] Backend not correctly configured")

if __name__ == "__main__":
    print("Running validation tests...")
    test_port_configuration()
    test_health_check_script()
    print("Validation tests completed.")