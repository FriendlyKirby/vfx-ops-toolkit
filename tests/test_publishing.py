import pytest
from pathlib import Path
from toolkit.publishing import publish_shot
from toolkit.publishing import PublishError
from toolkit.tracking.json_tracker import JsonTracker


def _touch(p: Path, size: int = 0) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * size)


def test_publish_shot_creates_record(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    _touch(renders / "frame_0001.exr", 10)
    _touch(renders / "frame_0002.exr", 10)
    _touch(renders / "frame_0004.exr", 10)

    tracker = JsonTracker(tmp_path / "tracking.json")

    result = publish_shot(
        shows_root=shows_root,
        show="demo_show",
        shot="shot010",
        version="v001",
        note="test publish",
        tracker=tracker,
        frame_prefix="frame_",
        frame_padding=4,
        frame_ext=".exr",
    )

    assert result.record.show == "demo_show"
    assert result.record.shot == "shot010"
    assert result.record.version == "v001"
    assert result.record.status == "warnings"
    assert result.record.missing_frames == [3]
    assert result.record.total_bytes == 30
    assert result.record.file_count == 3

    stored = tracker.list_publishes(show="demo_show", shot="shot010")
    assert len(stored) == 1

def test_publish_shot_raises_if_renders_missing(tmp_path: Path):
    shows_root = tmp_path / "shows"
    (shows_root / "demo_show" / "shots" / "shot010").mkdir(parents=True, exist_ok=True)

    tracker = JsonTracker(tmp_path / "tracking.json")

    with pytest.raises(PublishError):
        publish_shot(
            shows_root=shows_root,
            show="demo_show",
            shot="shot010",
            version="v001",
            note="",
            tracker=tracker,
            frame_prefix="frame_",
            frame_padding=4,
            frame_ext=".exr",
        )


def test_publish_shot_warns_if_no_frames(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    renders.mkdir(parents=True)

    tracker = JsonTracker(tmp_path / "tracking.json")

    result = publish_shot(
        shows_root=shows_root,
        show="demo_show",
        shot="shot010",
        version="v001",
        note="",
        tracker=tracker,
        frame_prefix="frame_",
        frame_padding=4,
        frame_ext=".exr",
    )

    assert result.record.frames_found == []
    assert result.record.missing_frames == []
    assert result.record.status == "warnings"
