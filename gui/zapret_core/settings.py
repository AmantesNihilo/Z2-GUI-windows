from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class GuiSettings:
    favorites: set[str] = field(default_factory=set)
    selected_targets: set[str] = field(default_factory=set)
    custom_presets: set[str] = field(default_factory=set)
    hidden_presets: set[str] = field(default_factory=set)
    theme: str = "dark"
    language: str = "en"
    close_winws_action: str = "ask"
    start_zapret_enabled: bool = True
    start_tg_ws_enabled: bool = False
    onboarding_seen: bool = False
    tg_ws_host: str = "127.0.0.1"
    tg_ws_port: int = 1443
    tg_ws_secret: str = field(default_factory=lambda: os.urandom(16).hex())
    tg_ws_pid: int = 0


def load_settings(path: Path) -> GuiSettings:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return GuiSettings()

    favorites = raw.get("favorites", [])
    if not isinstance(favorites, list):
        favorites = []
    selected_targets = raw.get("selected_targets", [])
    if not isinstance(selected_targets, list):
        selected_targets = []
    custom_presets = raw.get("custom_presets", [])
    if not isinstance(custom_presets, list):
        custom_presets = []
    hidden_presets = raw.get("hidden_presets", [])
    if not isinstance(hidden_presets, list):
        hidden_presets = []
    close_winws_action = str(raw.get("close_winws_action", "ask"))
    if close_winws_action not in {"ask", "stop", "keep"}:
        close_winws_action = "ask"
    language = str(raw.get("language", "en")).strip().lower()
    if language not in {"en", "ru"}:
        language = "en"
    tg_ws_port = _safe_int(raw.get("tg_ws_port", 1443), 1443)
    if not (1 <= tg_ws_port <= 65535):
        tg_ws_port = 1443
    tg_ws_secret = str(raw.get("tg_ws_secret", "")).strip()
    if len(tg_ws_secret) != 32:
        tg_ws_secret = os.urandom(16).hex()
    try:
        bytes.fromhex(tg_ws_secret)
    except ValueError:
        tg_ws_secret = os.urandom(16).hex()

    return GuiSettings(
        favorites={str(name) for name in favorites},
        selected_targets={str(name) for name in selected_targets},
        custom_presets={str(name) for name in custom_presets},
        hidden_presets={str(name) for name in hidden_presets},
        theme=str(raw.get("theme", "dark")),
        language=language,
        close_winws_action=close_winws_action,
        start_zapret_enabled=bool(raw.get("start_zapret_enabled", True)),
        start_tg_ws_enabled=bool(raw.get("start_tg_ws_enabled", False)),
        onboarding_seen=bool(raw.get("onboarding_seen", False)),
        tg_ws_host=str(raw.get("tg_ws_host", "127.0.0.1")).strip() or "127.0.0.1",
        tg_ws_port=tg_ws_port,
        tg_ws_secret=tg_ws_secret,
        tg_ws_pid=max(0, _safe_int(raw.get("tg_ws_pid", 0), 0)),
    )


def save_settings(path: Path, settings: GuiSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "favorites": sorted(settings.favorites, key=str.casefold),
        "selected_targets": sorted(settings.selected_targets, key=str.casefold),
        "custom_presets": sorted(settings.custom_presets, key=str.casefold),
        "hidden_presets": sorted(settings.hidden_presets, key=str.casefold),
        "theme": settings.theme,
        "language": settings.language,
        "close_winws_action": settings.close_winws_action,
        "start_zapret_enabled": settings.start_zapret_enabled,
        "start_tg_ws_enabled": settings.start_tg_ws_enabled,
        "onboarding_seen": settings.onboarding_seen,
        "tg_ws_host": settings.tg_ws_host,
        "tg_ws_port": settings.tg_ws_port,
        "tg_ws_secret": settings.tg_ws_secret,
        "tg_ws_pid": settings.tg_ws_pid,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
