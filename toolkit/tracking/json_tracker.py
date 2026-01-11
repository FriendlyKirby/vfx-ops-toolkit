from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .base import PublishRecord


class JsonTracker:
    """
    Local JSON-backed tracker. Simulates a production tracking system.
    Stores a list of publish records in a JSON file.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return data

    def _save(self, rows: list[dict]) -> None:
        self.path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def record_publish(self, record: PublishRecord) -> None:
        rows = self._load()
        rows.append(asdict(record))
        self._save(rows)

    def list_publishes(self, show: Optional[str] = None, shot: Optional[str] = None) -> list[PublishRecord]:
        rows = self._load()
        records: list[PublishRecord] = []
        for r in rows:
            try:
                rec = PublishRecord(**r)
            except TypeError:
                continue

            if show and rec.show != show:
                continue
            if shot and rec.shot != shot:
                continue
            records.append(rec)

        # newest first
        records.sort(key=lambda x: x.timestamp_utc, reverse=True)
        return records
