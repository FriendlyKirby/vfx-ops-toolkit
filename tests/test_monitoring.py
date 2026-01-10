from pathlib import Path

from toolkit.monitoring import _dir_size_bytes, disk_usage_by_shot, format_bytes, bytes_to_mb


def _touch_with_size(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def test_dir_size_bytes_counts_recursive_files(tmp_path: Path):
    root = tmp_path / "renders"
    _touch_with_size(root / "a.exr", 10)
    _touch_with_size(root / "sub" / "b.exr", 15)
    (root / "sub" / "empty_dir").mkdir(parents=True, exist_ok=True)

    total, count = _dir_size_bytes(root)
    assert total == 25
    assert count == 2


def test_format_bytes_basic():
    assert format_bytes(0) == "0 B"
    assert format_bytes(1) == "1 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"


def test_disk_usage_by_shot_reports_expected_totals(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    _touch_with_size(renders / "frame_0001.exr", 100)
    _touch_with_size(renders / "frame_0002.exr", 200)

    results = disk_usage_by_shot(shows_root)
    assert len(results) == 1

    r = results[0]
    assert r.show == "demo_show"
    assert r.shot == "shot010"
    assert r.total_bytes == 300
    assert r.file_count == 2

def test_bytes_to_mb():
    assert bytes_to_mb(0) == 0.0
    assert bytes_to_mb(1024 * 1024) == 1.0