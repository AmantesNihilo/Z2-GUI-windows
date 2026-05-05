from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Preset:
    name: str
    path: Path


def natural_key(value: str) -> list[object]:
    parts = re.split(r"(\d+)", value.casefold())
    return [int(part) if part.isdigit() else part for part in parts]


def list_presets(presets_dir: Path) -> list[Preset]:
    if not presets_dir.exists():
        return []

    presets = [
        Preset(path.stem, path)
        for path in presets_dir.glob("*.txt")
        if not path.name.startswith("_")
    ]
    return sorted(presets, key=lambda preset: natural_key(preset.name))


def unique_destination(presets_dir: Path, source: Path) -> Path:
    candidate = presets_dir / source.name
    if not candidate.exists():
        return candidate

    index = 2
    while True:
        next_candidate = presets_dir / f"{source.stem} ({index}){source.suffix}"
        if not next_candidate.exists():
            return next_candidate
        index += 1


def add_preset(presets_dir: Path, source: Path) -> Preset:
    if source.suffix.casefold() != ".txt":
        raise ValueError("Preset file must be .txt")

    presets_dir.mkdir(parents=True, exist_ok=True)
    destination = unique_destination(presets_dir, source)
    shutil.copy2(source, destination)
    return Preset(destination.stem, destination)
