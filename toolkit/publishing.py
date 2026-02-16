from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .monitoring import _dir_size_bytes
from .validation import validate_renders
from .tracking.base import PublishRecord, Tracker

import json

class PublishError(RuntimeError):
    pass

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

    if not shot_root.exists():
        raise PublishError(f"Shot path not found: {shot_root}")

    if not render_dir.exists() or not render_dir.is_dir():
        raise PublishError(f"Renders directory not found: {render_dir}")

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
    if not frames_found or missing_frames:
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

def write_publish_manifest(*, publish_root: Path, shows_root: Path, record: PublishRecord) -> Path:
    """
    Write a publish manifest JSON file to:
      <publish_root>/<show>/<shot>/<version>/publish.json

    This simulates the kind of metadata artifact a pipeline might generate.
    """
    render_dir = shows_root / record.show / "shots" / record.shot / "renders"
    out_dir = publish_root / record.show / record.shot / record.version
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "publish.json"
    payload = {
        "schema": "vfx-ops-toolkit.publish_manifest",
        "record": asdict(record),
        "source_render_dir": str(render_dir),
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path
