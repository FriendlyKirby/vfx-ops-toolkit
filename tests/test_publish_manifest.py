import json
from pathlib import Path

from toolkit.publishing import publish_shot, write_publish_manifest
from toolkit.tracking.json_tracker import JsonTracker


def _touch(p: Path, size: int = 0) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * size)


def test_write_publish_manifest_creates_file(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    _touch(renders / "frame_0001.exr", 1024)
    _touch(renders / "frame_0002.exr", 2048)
    _touch(renders / "frame_0004.exr", 1024)

    tracker = JsonTracker(tmp_path / "tracking.json")

    result = publish_shot(
        shows_root=shows_root,
        show="demo_show",
        shot="shot010",
        version="v001",
        note="manifest test",
        tracker=tracker,
        frame_prefix="frame_",
        frame_padding=4,
        frame_ext=".exr",
    )

    publish_root = tmp_path / "published"
    manifest_path = write_publish_manifest(
        publish_root=publish_root,
        shows_root=shows_root,
        record=result.record,
    )

    assert manifest_path.exists()

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["schema"] == "vfx-ops-toolkit.publish_manifest"
    assert data["record"]["show"] == "demo_show"
    assert data["record"]["shot"] == "shot010"
    assert data["record"]["version"] == "v001"
    assert "source_render_dir" in data