#!/usr/bin/env python3

import subprocess
import sys
from dotenv import load_dotenv


def run_tests():
    load_dotenv()

    print("Running all tests with coverage...")
    command = [
        "pytest",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "--disable-warnings",
        "-v",
        "-s",
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
