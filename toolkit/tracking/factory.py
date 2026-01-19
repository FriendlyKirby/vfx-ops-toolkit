from __future__ import annotations
from pathlib import Path
from .base import Tracker
from .json_tracker import JsonTracker


def make_tracker(cfg: dict) -> Tracker:
    tracking_cfg = cfg.get("tracking", {}) if isinstance(cfg.get("tracking", {}), dict) else {}
    backend = tracking_cfg.get("backend", "json")

    if backend != "json":
        raise ValueError(f"Unsupported tracking backend: {backend}. Only 'json' is implemented.")

    json_path = tracking_cfg.get("json_path", "data/tracking_db.json")
    return JsonTracker(Path(json_path))