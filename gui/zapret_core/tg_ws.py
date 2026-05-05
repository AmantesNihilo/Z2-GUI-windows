from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

from .paths import AppPaths


CREATE_NO_WINDOW = 0x08000000


def proxy_link(host: str, port: int, secret: str) -> str:
    return f"tg://proxy?server={host}&port={port}&secret=dd{secret}"


def log_file(paths: AppPaths) -> Path:
    return paths.utils_dir / "tg-ws-proxy.log"


def is_port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    completed = subprocess.run(
        ["tasklist.exe", "/FI", f"PID eq {pid}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
        creationflags=CREATE_NO_WINDOW,
    )
    text = ((completed.stdout or "") + (completed.stderr or "")).lower()
    return str(pid) in text and "no tasks" not in text and "информация:" not in text


def is_running(host: str, port: int, pid: int = 0) -> bool:
    return is_pid_running(pid)


def start(paths: AppPaths, host: str, port: int, secret: str) -> subprocess.Popen:
    if is_port_open(host, port):
        raise RuntimeError(f"tg-ws port is already in use: {host}:{port}")

    paths.utils_dir.mkdir(parents=True, exist_ok=True)
    command = _helper_command(paths, host, port, secret)
    return subprocess.Popen(
        command,
        cwd=str(paths.root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )


def stop(pid: int, host: str, port: int) -> None:
    if pid > 0:
        subprocess.run(
            ["taskkill.exe", "/F", "/PID", str(pid), "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            creationflags=CREATE_NO_WINDOW,
        )
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if not is_port_open(host, port):
            return
        time.sleep(0.1)


def _helper_command(paths: AppPaths, host: str, port: int, secret: str) -> list[str]:
    args = [
        "--z2-tg-ws-proxy",
        "--host",
        host,
        "--port",
        str(port),
        "--secret",
        secret,
        "--log-file",
        str(log_file(paths)),
    ]
    if getattr(sys, "frozen", False):
        return [sys.executable, *args]
    return [sys.executable, str(paths.root / "gui" / "app.py"), *args]
