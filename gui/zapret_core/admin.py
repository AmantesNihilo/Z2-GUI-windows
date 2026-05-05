from __future__ import annotations

import ctypes
import sys
from pathlib import Path


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(script: Path) -> bool:
    executable = gui_python_executable()
    params = " ".join([f'"{script}"', *[f'"{arg}"' for arg in sys.argv[1:]]])
    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        params,
        str(script.parent),
        1,
    )
    return result > 32


def gui_python_executable() -> str:
    executable = Path(sys.executable)
    if executable.name.casefold() == "python.exe":
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    return str(executable)
