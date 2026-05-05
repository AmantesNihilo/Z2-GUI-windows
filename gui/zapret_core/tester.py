from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass

from .targets import Target


CREATE_NO_WINDOW = 0x08000000


@dataclass(frozen=True)
class TargetResult:
    name: str
    http_tokens: tuple[str, ...]
    ping_ok: bool
    ping_text: str


@dataclass(frozen=True)
class PresetTestResult:
    ok: int
    fail: int
    unsup: int
    ping_ok: int
    ping_total: int
    details: tuple[TargetResult, ...]


def test_url(url: str, timeout_sec: int) -> tuple[str, ...]:
    tests = (
        ("HTTP", ("--http1.1",)),
        ("TLS1.2", ("--tlsv1.2", "--tls-max", "1.2")),
        ("TLS1.3", ("--tlsv1.3", "--tls-max", "1.3")),
    )
    tokens: list[str] = []

    for label, protocol_args in tests:
        command = [
            "curl.exe",
            "-I",
            "-s",
            "-m",
            str(timeout_sec),
            "-o",
            "NUL",
            "-w",
            "%{http_code}",
            "--show-error",
            *protocol_args,
            url,
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_sec + 3,
                check=False,
                creationflags=CREATE_NO_WINDOW,
            )
        except (OSError, subprocess.TimeoutExpired):
            tokens.append(f"{label}:ERR")
            continue

        stderr = completed.stderr or ""
        unsupported = completed.returncode == 35 or re.search(
            r"not supported|unsupported protocol|schannel",
            stderr,
            re.IGNORECASE,
        )
        if unsupported:
            tokens.append(f"{label}:UNSUP")
        elif re.search(r"certificate|SSL|self.?signed", stderr, re.IGNORECASE):
            tokens.append(f"{label}:SSL")
        elif completed.returncode == 0:
            tokens.append(f"{label}:OK")
        else:
            tokens.append(f"{label}:FAIL")

    return tuple(tokens)


def test_ping(target: str | None, timeout_sec: int) -> tuple[bool, str]:
    if not target:
        return False, "n/a"

    try:
        completed = subprocess.run(
            ["ping.exe", "-n", "2", "-w", str(timeout_sec * 1000), target],
            capture_output=True,
            text=True,
            timeout=timeout_sec * 2 + 3,
            check=False,
            creationflags=CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, "Timeout"

    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0:
        return False, "Timeout"

    avg_match = re.search(r"Average\s*=\s*(\d+ms)", output, re.IGNORECASE)
    if not avg_match:
        avg_match = re.search(r"Среднее\s*=\s*(\d+мс)", output, re.IGNORECASE)
    return True, avg_match.group(1) if avg_match else "OK"


ProgressCallback = Callable[[Target, TargetResult, int, int], None]
StopCallback = Callable[[], bool]


def test_targets(
    targets: list[Target],
    timeout_sec: int,
    progress_callback: ProgressCallback | None = None,
    stop_callback: StopCallback | None = None,
) -> PresetTestResult:
    details: list[TargetResult] = []
    ok = fail = unsup = ping_ok = ping_total = 0

    for index, target in enumerate(targets, start=1):
        if stop_callback is not None and stop_callback():
            break
        tokens = test_url(target.url, timeout_sec) if target.url else tuple()
        if stop_callback is not None and stop_callback():
            break
        for token in tokens:
            if token.endswith(":OK"):
                ok += 1
            elif token.endswith(":UNSUP"):
                unsup += 1
            else:
                fail += 1

        ping_success, ping_text = test_ping(target.ping_target, timeout_sec)
        if target.ping_target:
            ping_total += 1
            if ping_success:
                ping_ok += 1

        target_result = TargetResult(target.name, tokens, ping_success, ping_text)
        details.append(target_result)
        if progress_callback is not None:
            progress_callback(target, target_result, index, len(targets))

    return PresetTestResult(ok, fail, unsup, ping_ok, ping_total, tuple(details))
