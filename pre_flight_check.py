#!/usr/bin/env python3
"""
Pre-Flight Verification Script
Checks system readiness before deploying Version 2.0

Usage: python pre_flight_check.py
"""

import os
import sys
import time
import requests
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    print(f"{BLUE}ℹ{RESET} {text}")

class PreFlightChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warning = 0
        self.critical_failures = []

    def check_environment_variables(self):
        """Check required environment variables are set"""
        print_header("Environment Variables")

        # Check OPENROUTER_API_KEY
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            if api_key.startswith("sk-or-") or api_key.startswith("sk-or-v1-"):
                print_success(f"OPENROUTER_API_KEY is set and valid (starts with {api_key[:10]}...)")
                self.checks_passed += 1
            else:
                print_error("OPENROUTER_API_KEY is set but doesn't start with 'sk-or-' or 'sk-or-v1-'")
                self.checks_failed += 1
                self.critical_failures.append("Invalid OPENROUTER_API_KEY format")
        else:
            print_error("OPENROUTER_API_KEY is not set")
            self.checks_failed += 1
            self.critical_failures.append("OPENROUTER_API_KEY not set")

        # Check OPENROUTER_MODEL
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        print_info(f"OPENROUTER_MODEL: {model}")

    def check_files_exist(self):
        """Check required files exist"""
        print_header("File System")

        required_files = [
            "backend/src/services/agent.py",
            "backend/src/main.py",
            "backend/requirements.txt",
            "COMPREHENSIVE_FIX_SUMMARY.md",
            "DEPLOYMENT_CHECKLIST.md",
            "QUICK_START_GUIDE.md",
            "PRODUCTION_RUNBOOK.md",
            "RELEASE_NOTES.md"
        ]

        for file_path in required_files:
            if Path(file_path).exists():
                print_success(f"{file_path} exists")
                self.checks_passed += 1
            else:
                print_error(f"{file_path} not found")
                self.checks_failed += 1
                if "agent.py" in file_path or "main.py" in file_path:
                    self.critical_failures.append(f"Critical file missing: {file_path}")

    def check_backend_running(self):
        """Check if backend is running"""
        print_header("Backend Service")

        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend is running on port 8001")
                self.checks_passed += 1
                return True
            else:
                print_error(f"Backend returned status code {response.status_code}")
                self.checks_failed += 1
                return False
        except requests.exceptions.ConnectionError:
            print_error("Backend is not running on port 8001")
            self.checks_failed += 1
            self.critical_failures.append("Backend not running")
            return False
        except Exception as e:
            print_error(f"Error checking backend: {str(e)}")
            self.checks_failed += 1
            return False

    def check_api_credits(self):
        """Check if OpenRouter API is accessible"""
        print_header("API Connectivity")

        # Try a simple chat request
        try:
            response = requests.post(
                "http://localhost:8001/api/preflight-test/chat",
                json={"message": "test"},
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    print_success("AI agent is available and responding")
                    self.checks_passed += 1
                    return True
                else:
                    print_warning("Backend responded but format unexpected")
                    self.checks_warning += 1
                    return False
            elif response.status_code == 402:
                print_error("OpenRouter API credits exhausted (HTTP 402)")
                self.checks_failed += 1
                self.critical_failures.append("API credits exhausted")
                print_info("Add credits at: https://openrouter.ai/settings/credits")
                return False
            else:
                print_error(f"Backend returned status code {response.status_code}")
                self.checks_failed += 1
                return False

        except requests.exceptions.Timeout:
            print_error("Request timed out (>20s)")
            self.checks_failed += 1
            return False
        except Exception as e:
            print_error(f"Error testing API: {str(e)}")
            self.checks_failed += 1
            return False

    def check_database(self):
        """Check database exists and is accessible"""
        print_header("Database")

        db_path = Path("backend/todo.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print_success(f"Database exists (size: {size_mb:.2f} MB)")
            self.checks_passed += 1

            # Check if database is writable
            if os.access(db_path, os.W_OK):
                print_success("Database is writable")
                self.checks_passed += 1
            else:
                print_error("Database is not writable")
                self.checks_failed += 1
                self.critical_failures.append("Database not writable")
        else:
            print_warning("Database does not exist (will be created on first use)")
            self.checks_warning += 1

    def check_test_scripts(self):
        """Check test scripts exist"""
        print_header("Test Scripts")

        test_scripts = [
            "test_env_check.py",
            "test_confirmation_fix.py",
            "comprehensive_test_suite.py"
        ]

        for script in test_scripts:
            if Path(script).exists():
                print_success(f"{script} exists")
                self.checks_passed += 1
            else:
                print_warning(f"{script} not found")
                self.checks_warning += 1

    def check_git_status(self):
        """Check git status"""
        print_header("Git Status")

        try:
            import subprocess

            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                branch = result.stdout.strip()
                print_info(f"Current branch: {branch}")

                if branch == "003-openrouter-auth-fix":
                    print_success("On correct deployment branch")
                    self.checks_passed += 1
                else:
                    print_warning(f"Not on deployment branch (expected: 003-openrouter-auth-fix)")
                    self.checks_warning += 1

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                changes = result.stdout.strip()
                if changes:
                    print_warning("Uncommitted changes detected")
                    self.checks_warning += 1
                    # Show first 5 changes
                    lines = changes.split('\n')[:5]
                    for line in lines:
                        print(f"  {line}")
                    if len(changes.split('\n')) > 5:
                        print(f"  ... and {len(changes.split('\n')) - 5} more")
                else:
                    print_success("No uncommitted changes")
                    self.checks_passed += 1

        except FileNotFoundError:
            print_warning("Git not found (skipping git checks)")
            self.checks_warning += 1
        except Exception as e:
            print_warning(f"Error checking git status: {str(e)}")
            self.checks_warning += 1

    def check_backups(self):
        """Check if backups directory exists"""
        print_header("Backups")

        backups_dir = Path("backups")
        if backups_dir.exists():
            print_success("Backups directory exists")
            self.checks_passed += 1

            # Count backup files
            backup_files = list(backups_dir.glob("*.db"))
            if backup_files:
                print_info(f"Found {len(backup_files)} database backup(s)")
                # Show most recent
                if backup_files:
                    latest = max(backup_files, key=lambda p: p.stat().st_mtime)
                    age_hours = (time.time() - latest.stat().st_mtime) / 3600
                    print_info(f"Most recent backup: {latest.name} ({age_hours:.1f} hours ago)")
            else:
                print_warning("No database backups found")
                self.checks_warning += 1
        else:
            print_warning("Backups directory does not exist")
            self.checks_warning += 1
            print_info("Create with: mkdir backups")

    def print_summary(self):
        """Print summary of checks"""
        print_header("Pre-Flight Check Summary")

        total_checks = self.checks_passed + self.checks_failed + self.checks_warning

        print(f"Total checks: {total_checks}")
        print(f"{GREEN}Passed: {self.checks_passed}{RESET}")
        print(f"{RED}Failed: {self.checks_failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.checks_warning}{RESET}")

        if self.critical_failures:
            print(f"\n{RED}Critical Failures:{RESET}")
            for failure in self.critical_failures:
                print(f"  • {failure}")

        print()

        if self.checks_failed == 0:
            if self.checks_warning == 0:
                print(f"{GREEN}✓ All checks passed! System is ready for deployment.{RESET}")
                return True
            else:
                print(f"{YELLOW}⚠ All critical checks passed, but there are warnings.{RESET}")
                print(f"{YELLOW}  Review warnings before proceeding with deployment.{RESET}")
                return True
        else:
            print(f"{RED}✗ Pre-flight checks failed. Fix critical issues before deployment.{RESET}")
            return False

    def run_all_checks(self):
        """Run all pre-flight checks"""
        print_header("Todo AI Chatbot - Pre-Flight Verification")
        print_info("Version 2.0 Deployment Readiness Check")
        print_info(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        self.check_environment_variables()
        self.check_files_exist()
        backend_running = self.check_backend_running()

        if backend_running:
            self.check_api_credits()
        else:
            print_warning("Skipping API checks (backend not running)")
            self.checks_warning += 1

        self.check_database()
        self.check_test_scripts()
        self.check_git_status()
        self.check_backups()

        return self.print_summary()

def main():
    """Main entry point"""
    checker = PreFlightChecker()

    try:
        ready = checker.run_all_checks()

        if ready:
            print(f"\n{GREEN}Next Steps:{RESET}")
            print("1. Review DEPLOYMENT_CHECKLIST.md")
            print("2. Run comprehensive tests: python comprehensive_test_suite.py")
            print("3. Follow deployment procedures")
            sys.exit(0)
        else:
            print(f"\n{RED}Action Required:{RESET}")
            print("1. Fix critical failures listed above")
            print("2. Re-run this script: python pre_flight_check.py")
            print("3. See QUICK_START_GUIDE.md for help")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Pre-flight check interrupted by user{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {str(e)}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
