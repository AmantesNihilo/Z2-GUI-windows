from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class AppPaths:
    root: Path
    presets_dir: Path
    utils_dir: Path
    exe_dir: Path
    winws2_exe: Path
    active_preset: Path
    current_preset: Path
    targets_file: Path
    gui_settings: Path
    gui_results: Path

    @classmethod
    def from_app_file(cls, app_file: Path) -> "AppPaths":
        if getattr(sys, "frozen", False):
            root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        else:
            root = app_file.resolve().parents[1]
        utils_dir = root / "utils"
        exe_dir = root / "exe"
        return cls(
            root=root,
            presets_dir=root / "presets",
            utils_dir=utils_dir,
            exe_dir=exe_dir,
            winws2_exe=exe_dir / "winws2.exe",
            active_preset=utils_dir / "preset-active.txt",
            current_preset=utils_dir / "current_preset.txt",
            targets_file=utils_dir / "targets.txt",
            gui_settings=utils_dir / "gui-settings.json",
            gui_results=utils_dir / "gui-results.json",
        )
