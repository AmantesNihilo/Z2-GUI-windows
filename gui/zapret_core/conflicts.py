from __future__ import annotations

import csv
import io
import subprocess
from dataclasses import dataclass


CREATE_NO_WINDOW = 0x08000000


CONFLICT_PROCESS_NAMES = {
    "happ.exe",
    "hiddify.exe",
    "nekobox.exe",
    "nekoray.exe",
    "v2rayn.exe",
    "v2ray.exe",
    "xray.exe",
    "clash.exe",
    "clash-verge.exe",
    "clash verge.exe",
    "clash-meta.exe",
    "sing-box.exe",
    "singbox.exe",
    "mihomo.exe",
    "wireguard.exe",
    "openvpn.exe",
    "openvpn-gui.exe",
    "outline.exe",
    "shadowsocks.exe",
    "shadowsocksr.exe",
    "sstap.exe",
    "proxifier.exe",
}


@dataclass(frozen=True)
class ConflictProcess:
    image_name: str
    pid: int
    session_name: str = ""
    memory: str = ""

    @property
    def display_name(self) -> str:
        details = f"PID {self.pid}"
        if self.memory:
            details += f", {self.memory}"
        return f"{self.image_name} ({details})"


def find_conflicts() -> list[ConflictProcess]:
    completed = subprocess.run(
        ["tasklist.exe", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
        creationflags=CREATE_NO_WINDOW,
    )
    output = completed.stdout or ""
    found: list[ConflictProcess] = []

    for row in csv.reader(io.StringIO(output)):
        if len(row) < 2:
            continue
        image_name = row[0].strip()
        image_key = image_name.casefold()
        if image_key not in CONFLICT_PROCESS_NAMES:
            continue
        try:
            pid = int(row[1])
        except ValueError:
            continue
        found.append(
            ConflictProcess(
                image_name=image_name,
                pid=pid,
                session_name=row[2].strip() if len(row) > 2 else "",
                memory=row[4].strip() if len(row) > 4 else "",
            )
        )

    return sorted(found, key=lambda process: (process.image_name.casefold(), process.pid))


def kill_processes(processes: list[ConflictProcess]) -> None:
    for process in processes:
        subprocess.run(
            ["taskkill.exe", "/F", "/PID", str(process.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            creationflags=CREATE_NO_WINDOW,
        )
