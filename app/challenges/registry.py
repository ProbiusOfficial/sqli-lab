from __future__ import annotations

from typing import Iterable

from app.challenges.levels import ALL_CHALLENGES


def iter_challenges() -> Iterable:
    return ALL_CHALLENGES


def get_challenge(level_id: str):
    for c in ALL_CHALLENGES:
        if c.level_id == level_id:
            return c
    return ALL_CHALLENGES[0]
