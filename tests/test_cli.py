import subprocess
import sys
from pathlib import Path


def _touch(p: Path, size: int = 0) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * size)


def test_cli_validate_exit_code_missing_frames(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    _touch(renders / "frame_0001.exr")
    _touch(renders / "frame_0002.exr")
    _touch(renders / "frame_0004.exr")

    (tmp_path / "toolkit.yaml").write_text(
        f'shows_root: "{shows_root.as_posix()}"\n'
        "naming:\n"
        "  frame_prefix: \"frame_\"\n"
        "  frame_padding: 4\n"
        "  frame_ext: \".exr\"\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, "-m", "toolkit", "validate"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "Missing frames" in proc.stdout


def test_cli_publish_creates_tracking_file(tmp_path: Path):
    shows_root = tmp_path / "shows"
    renders = shows_root / "demo_show" / "shots" / "shot010" / "renders"
    _touch(renders / "frame_0001.exr", 10)
    _touch(renders / "frame_0002.exr", 10)
    _touch(renders / "frame_0004.exr", 10)

    data_dir = tmp_path / "data"
    db_path = data_dir / "tracking_db.json"

    (tmp_path / "toolkit.yaml").write_text(
        f'shows_root: "{shows_root.as_posix()}"\n'
        "naming:\n"
        "  frame_prefix: \"frame_\"\n"
        "  frame_padding: 4\n"
        "  frame_ext: \".exr\"\n"
        "tracking:\n"
        "  backend: \"json\"\n"
        f'  json_path: "{db_path.as_posix()}"\n',
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable, "-m", "toolkit", "publish",
            "--show", "demo_show",
            "--shot", "shot010",
            "--version", "v001",
            "--note", "test",
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert db_path.exists()
    assert "Publish recorded" in proc.stdout
