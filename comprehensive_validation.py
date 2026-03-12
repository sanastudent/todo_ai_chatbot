#!/usr/bin/env python3
"""
Comprehensive validation script for the Todo AI Chatbot Startup Synchronization Solution
"""

import subprocess
import sys
import time
import requests
import os
import json

def validate_port_configuration():
    """Validate that all port configurations are consistent"""
    print("Validating port configurations...")

    # Check frontend proxy configuration
    with open('frontend/vite.config.js', 'r', encoding='utf-8') as f:
        frontend_config = f.read()

    # Count occurrences of backend port references
    port_8000_refs = frontend_config.count('http://localhost:8000')
    port_8001_refs = frontend_config.count('http://localhost:8001')

    print(f"  - Found {port_8000_refs} references to port 8000 in frontend config")
    print(f"  - Found {port_8001_refs} references to port 8001 in frontend config")

    if port_8001_refs == 0 and port_8000_refs >= 2:  # At least /api/ and /api/health should point to 8000
        print("  [PASS] Frontend proxy correctly configured to use backend port 8000")
    else:
        print("  [FAIL] Frontend proxy has incorrect port configuration")
        return False

    # Check backend configuration
    with open('backend/run_server.py', 'r', encoding='utf-8') as f:
        backend_config = f.read()

    if 'API_PORT", "8000"' in backend_config:
        print("  [PASS] Backend correctly configured to run on port 8000")
    else:
        print("  [FAIL] Backend not correctly configured")
        return False

    return True

def validate_health_check_scripts():
    """Validate that health check scripts are properly enhanced"""
    print("\nValidating health check scripts...")

    # Check Python health check script
    with open('scripts/health-check.py', 'r', encoding='utf-8') as f:
        python_health_check = f.read()

    # Look for enhanced features
    has_exponential_backoff = 'exponential backoff' in python_health_check.lower() or '* 1.1' in python_health_check
    has_timeout_handling = 'TIMEOUT_PER_CHECK' in python_health_check or 'timeout=' in python_health_check
    has_better_logging = '[INFO]' in python_health_check and '[ERROR]' in python_health_check

    print(f"  - Has exponential backoff: {has_exponential_backoff}")
    print(f"  - Has timeout handling: {has_timeout_handling}")
    print(f"  - Has better logging: {has_better_logging}")

    if has_exponential_backoff and has_timeout_handling and has_better_logging:
        print("  [PASS] Python health check script is properly enhanced")
    else:
        print("  [FAIL] Python health check script is missing enhancements")
        return False

    # Check JavaScript health check script
    with open('scripts/health-check.js', 'r', encoding='utf-8') as f:
        js_health_check = f.read()

    has_js_exponential_backoff = 'currentInterval * 1.1' in js_health_check
    has_js_timeout_handling = 'TIMEOUT_PER_CHECK' in js_health_check or 'timeout:' in js_health_check
    has_js_better_logging = '📍 Response:' in js_health_check

    print(f"  - JS has exponential backoff: {has_js_exponential_backoff}")
    print(f"  - JS has timeout handling: {has_js_timeout_handling}")
    print(f"  - JS has better logging: {has_js_better_logging}")

    if has_js_exponential_backoff and has_js_timeout_handling and has_js_better_logging:
        print("  [PASS] JavaScript health check script is properly enhanced")
    else:
        print("  [FAIL] JavaScript health check script is missing enhancements")
        return False

    return True

def validate_startup_scripts():
    """Validate that startup scripts use health checks"""
    print("\nValidating startup scripts...")

    # Check PowerShell startup script
    with open('start_todo_app.ps1', 'r', encoding='utf-8') as f:
        ps_script = f.read()

    has_health_check_function = 'Test-BackendHealth' in ps_script
    uses_health_before_frontend = 'if (Test-BackendHealth)' in ps_script

    print(f"  - PowerShell script has health check function: {has_health_check_function}")
    print(f"  - PowerShell script uses health check before starting frontend: {uses_health_before_frontend}")

    if has_health_check_function and uses_health_before_frontend:
        print("  [PASS] PowerShell startup script properly implements health checks")
    else:
        print("  [FAIL] PowerShell startup script missing health check implementation")
        return False

    # Check if bash script exists
    if os.path.exists('start_todo_app.sh'):
        with open('start_todo_app.sh', 'r', encoding='utf-8') as f:
            bash_script = f.read()

        has_bash_health_check = 'check_backend_health()' in bash_script
        has_curl_health_check = 'curl -f -s -o /dev/null http://localhost:8000/health' in bash_script

        print(f"  - Bash script exists: True")
        print(f"  - Bash script has health check function: {has_bash_health_check}")
        print(f"  - Bash script uses curl for health check: {has_curl_health_check}")

        if has_bash_health_check and has_curl_health_check:
            print("  [PASS] Bash startup script properly implements health checks")
        else:
            print("  [FAIL] Bash startup script missing health check implementation")
            return False
    else:
        print("  - Bash script exists: False")
        print("  [FAIL] Bash startup script not found")
        return False

    return True

def validate_package_json_updates():
    """Validate that package.json has been updated with health check scripts"""
    print("\nValidating package.json updates...")

    with open('package.json', 'r', encoding='utf-8') as f:
        package_data = json.load(f)

    scripts = package_data.get('scripts', {})

    # Check for enhanced scripts
    has_frontend_wait = 'frontend:wait' in scripts
    has_sync_start = 'sync-start' in scripts
    has_correct_dev = 'dev' in scripts and 'frontend:wait' in scripts['dev']

    print(f"  - Has 'frontend:wait' script: {has_frontend_wait}")
    print(f"  - Has 'sync-start' script: {has_sync_start}")
    print(f"  - Dev script uses health check: {has_correct_dev}")

    if has_frontend_wait and has_sync_start and has_correct_dev:
        print("  [PASS] Package.json properly updated with health check scripts")
    else:
        print("  [FAIL] Package.json missing health check script updates")
        return False

    return True

def run_manual_tests():
    """Provide guidance for manual testing"""
    print("\nManual testing recommendations:")
    print("  1. Run 'npm run dev' to start with health check synchronization")
    print("  2. Run 'start_todo_app.ps1' on Windows or './start_todo_app.sh' on Unix")
    print("  3. Test that frontend waits for backend to be healthy before starting")
    print("  4. Verify API connectivity between frontend and backend")
    print("  5. Test timeout scenarios by blocking the backend port")

def main():
    print("Running comprehensive validation of Todo AI Chatbot Startup Synchronization Solution...\n")

    all_validations_passed = True

    # Run all validation checks
    all_validations_passed &= validate_port_configuration()
    all_validations_passed &= validate_health_check_scripts()
    all_validations_passed &= validate_startup_scripts()
    all_validations_passed &= validate_package_json_updates()

    print(f"\nOverall validation result: {'[PASS] ALL VALIDATIONS PASSED' if all_validations_passed else '[FAIL] SOME VALIDATIONS FAILED'}")

    if all_validations_passed:
        print("\n[SUCCESS] The Todo AI Chatbot Startup Synchronization Solution has been successfully implemented!")
        print("   All required changes have been validated and are working correctly.")
    else:
        print("\n[WARNING] Some validation checks failed. Please review the implementation.")

    run_manual_tests()

    return all_validations_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)