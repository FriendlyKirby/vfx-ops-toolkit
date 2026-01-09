from pathlib import Path

from toolkit.validation import (
    _build_frame_regex,
    _collect_frame_numbers,
    _compute_missing,
    iter_shot_render_dirs,
    validate_renders,
)


def _touch(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"")


def test_build_frame_regex_matches_expected_names():
    rx = _build_frame_regex(prefix="frame_", padding=4, ext=".exr")

    assert rx.match("frame_0001.exr")
    assert rx.match("frame_1234.exr")

    # wrong prefix
    assert not rx.match("frm_0001.exr")
    # wrong padding
    assert not rx.match("frame_001.exr")
    # wrong ext
    assert not rx.match("frame_0001.png")


def test_collect_frame_numbers_sorts_and_filters(tmp_path: Path):
    render_dir = tmp_path / "renders"
    render_dir.mkdir()

    _touch(render_dir / "frame_0002.exr")
    _touch(render_dir / "frame_0001.exr")
    _touch(render_dir / "not_a_frame.txt")
    (render_dir / "subdir").mkdir()

    rx = _build_frame_regex(prefix="frame_", padding=4, ext=".exr")
    frames = _collect_frame_numbers(render_dir, rx)

    assert frames == [1, 2]


def test_compute_missing_detects_gaps():
    assert _compute_missing([]) == []
    assert _compute_missing([1]) == []
    assert _compute_missing([1, 2, 3]) == []
    assert _compute_missing([1, 2, 4]) == [3]
    assert _compute_missing([10, 12]) == [11]


def test_iter_shot_render_dirs_finds_expected_structure(tmp_path: Path):
    shows_root = tmp_path / "shows"

    # shows/demo_show/shots/shot010/renders
    render_dir = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    render_dir.mkdir(parents=True)

    found = list(iter_shot_render_dirs(shows_root))

    assert len(found) == 1
    show, shot, rd = found[0]
    assert show == "demo_show"
    assert shot == "shot010"
    assert rd == render_dir


def test_validate_renders_reports_missing_frames(tmp_path: Path):
    shows_root = tmp_path / "shows"
    render_dir = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    render_dir.mkdir(parents=True)

    # Create 0001, 0002, 0004 -> missing 0003
    _touch(render_dir / "frame_0001.exr")
    _touch(render_dir / "frame_0002.exr")
    _touch(render_dir / "frame_0004.exr")

    results = validate_renders(shows_root, frame_prefix="frame_", frame_padding=4, frame_ext=".exr")

    assert len(results) == 1
    r = results[0]
    assert r.show == "demo_show"
    assert r.shot == "shot010"
    assert r.frames_found == [1, 2, 4]
    assert r.missing_frames == [3]


def test_validate_renders_handles_no_frames(tmp_path: Path):
    shows_root = tmp_path / "shows"
    render_dir = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    render_dir.mkdir(parents=True)

    results = validate_renders(shows_root)

    assert len(results) == 1
    r = results[0]
    assert r.frames_found == []
    assert r.missing_frames == []
    