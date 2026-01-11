from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .monitoring import _dir_size_bytes
from .validation import validate_renders
from .tracking.base import PublishRecord, Tracker

@dataclass(frozen=True)
class PublishResult:
    record: PublishRecord

def publish_shot(
    *,
    shows_root: Path,
    show: str,
    shot: str,
    version: str,
    note: str,
    tracker: Tracker,
    frame_prefix: str,
    frame_padding: int,
    frame_ext: str,
) -> PublishResult:
    """
    Simulate publishing a shot:
    - validate frames for that shot
    - compute disk usage for that shot's renders folder
    - write a publish record via tracker
    No file moves/deletes.
    """
    shot_root = shows_root / show / "shots" / shot
    render_dir = shot_root / "renders"

    frames_found: list[int] = []
    missing_frames: list[int] = []
    total_bytes = 0
    file_count = 0

    all_results = validate_renders(
        shows_root,
        frame_prefix=frame_prefix,
        frame_padding=frame_padding,
        frame_ext=frame_ext,
    )
    for r in all_results:
        if r.show == show and r.shot == shot:
            frames_found = r.frames_found
            missing_frames = r.missing_frames
            break

    # Disk usage for renders
    total_bytes, file_count = _dir_size_bytes(render_dir)

    status = "ok"
    if missing_frames:
        status = "warnings"

    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    record = PublishRecord(
        show=show,
        shot=shot,
        version=version,
        status=status,
        note=note,
        timestamp_utc=ts,
        frames_found=frames_found,
        missing_frames=missing_frames,
        total_bytes=total_bytes,
        file_count=file_count,
    )
    tracker.record_publish(record)
    return PublishResult(record=record)
