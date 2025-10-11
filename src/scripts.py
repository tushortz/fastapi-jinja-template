"""Scripts for development tasks."""

import subprocess
import sys
from pathlib import Path


def format_code() -> None:
    """Format code using black."""
    src_path = Path(__file__).parent
    subprocess.run([sys.executable, "-m", "black", str(src_path)], check=True)


def lint_code() -> None:
    """Lint code using ruff."""
    src_path = Path(__file__).parent
    subprocess.run([sys.executable, "-m", "ruff", "check", str(src_path)], check=True)


def lint_fix() -> None:
    """Fix linting issues using ruff."""
    src_path = Path(__file__).parent
    subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(src_path), "--fix"], check=True
    )


def run_tests() -> None:
    """Run tests using pytest."""
    subprocess.run([sys.executable, "-m", "pytest"], check=True)


def run_dev_server() -> None:
    """Run development server using uvicorn."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        check=True,
    )
