from __future__ import annotations

import json
from pathlib import Path


ResultTuple = tuple[int, int, int, int, int, int]


def load_results(path: Path) -> dict[str, ResultTuple]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

    loaded: dict[str, ResultTuple] = {}
    if not isinstance(raw, dict):
        return loaded

    for name, value in raw.items():
        if not isinstance(value, dict):
            continue
        try:
            loaded[str(name)] = (
                int(value.get("ok", 0)),
                int(value.get("fail", 0)),
                int(value.get("unsup", 0)),
                int(value.get("ping_ok", 0)),
                int(value.get("ping_total", 0)),
                int(value.get("score", 0)),
            )
        except (TypeError, ValueError):
            continue
    return loaded


def save_results(path: Path, results: dict[str, ResultTuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        name: {
            "ok": ok,
            "fail": fail,
            "unsup": unsup,
            "ping_ok": ping_ok,
            "ping_total": ping_total,
            "score": score,
        }
        for name, (ok, fail, unsup, ping_ok, ping_total, score) in sorted(
            results.items(), key=lambda item: item[0].casefold()
        )
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
