"""Local dev launcher for running backend and frontend together.

Usage:
    python main.py

This starts:
- backend at http://127.0.0.1:8000
- frontend at http://127.0.0.1:8080
"""

from __future__ import annotations

import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def _start_process(module_app: str, port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            module_app,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--reload",
        ],
        cwd=str(PROJECT_ROOT),
    )


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    backend_process = _start_process("backend.main:app", 8000)
    frontend_process = _start_process("frontend.main:app", 8080)

    print("Started backend:  http://127.0.0.1:8000")
    print("Started frontend: http://127.0.0.1:8080")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            if backend_process.poll() is not None:
                print("Backend server exited unexpectedly.")
                return 1
            if frontend_process.poll() is not None:
                print("Frontend server exited unexpectedly.")
                return 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        _stop_process(frontend_process)
        _stop_process(backend_process)

    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    raise SystemExit(main())
