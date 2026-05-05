from __future__ import annotations


def score_result(ok: int, fail: int, ping_ok: int) -> int:
    return ok * 10 + ping_ok - fail * 2
