#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path


def load_env_file():
    try:
        from dotenv import load_dotenv
        
        env_file = Path(".env")
        if env_file.exists():
            print(f"Loading environment variables from {env_file}")
            load_dotenv(env_file)
            return True
        else:
            print("No .env file found")
            return False
    except ImportError:
        print("Warning: python-dotenv not installed. Skipping .env file loading.")
        return False


def check_credentials():
    test_prn = os.getenv("TEST_PRN")
    test_password = os.getenv("TEST_PASSWORD")
    
    return bool(test_prn and test_password)


def run_tests():
    load_env_file()

    has_credentials = check_credentials()
    
    if has_credentials:
        print("Running all tests with coverage...")
        command = [
            "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "--disable-warnings",
            "-v",
            "-s"
        ]
    else:
        print("Secrets missing. Running only tests not requiring secrets...")
        command = [
            "pytest",
            "-m", "not secret_required",
            "--disable-warnings",
            "-v",
            "-s"
        ]
    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please ensure pytest is installed.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 