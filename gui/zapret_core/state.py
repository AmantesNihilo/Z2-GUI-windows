from __future__ import annotations

from pathlib import Path


def read_current_preset(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig").strip()
    except FileNotFoundError:
        return ""


def write_current_preset(path: Path, name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(name.strip() + "\n", encoding="utf-8")
