from pathlib import Path

from toolkit.tracking.base import PublishRecord
from toolkit.tracking.json_tracker import JsonTracker


def test_json_tracker_records_and_lists(tmp_path: Path):
    db = tmp_path / "tracking_db.json"
    tracker = JsonTracker(db)

    rec = PublishRecord(
        show="demo_show",
        shot="shot010",
        version="v001",
        status="ok",
        note="test",
        timestamp_utc="2026-01-01T00:00:00Z",
        frames_found=[1, 2],
        missing_frames=[],
        total_bytes=123,
        file_count=2,
    )
    tracker.record_publish(rec)

    rows = tracker.list_publishes()
    assert len(rows) == 1
    assert rows[0].show == "demo_show"
    assert rows[0].shot == "shot010"
    assert rows[0].version == "v001"
