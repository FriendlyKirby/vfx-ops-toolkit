from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Optional


@dataclass(frozen=True)
class PublishRecord:
    show: str
    shot: str
    version: str
    status: str  # e.g. "ok", "warnings", "failed"
    note: str
    timestamp_utc: str
    frames_found: list[int]
    missing_frames: list[int]
    total_bytes: int
    file_count: int


class Tracker(Protocol):
    def record_publish(self, record: PublishRecord) -> None: ...
    def list_publishes(self, show: Optional[str] = None, shot: Optional[str] = None) -> list[PublishRecord]: ...
