from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

@dataclass(frozen=True)
class ShotValidationResult:
    """Validation result for one shot render directory"""
    show: str
    shot: str
    render_dir: Path
    frames_found: list[int]
    missing_frames: list[int]

def _build_frame_regex(prefix: str, padding: int, ext: str) -> re.Pattern:
    """
    Return a compiled regex for frame files; group 1 captures the frame number
    """
    ext_escaped = re.escape(ext)
    return re.compile(rf"^{re.escape(prefix)}(\d{{{padding}}}){ext_escaped}$")

def _collect_frame_numbers(render_dir: Path, frame_re: re.Pattern) -> list[int]:
    """
    Return sorted frame unmbers found in render_dir matching frame_re
    """
    frames: list[int] = []
    for p in render_dir.iterdir():
        if not p.is_file():
            continue
        m = frame_re.match(p.name)
        if not m:
            continue
        frames.append(int(m.group(1)))
    frames.sort()
    return frames

def _compute_missing(frames: list[int]) -> list[int]:
    """
    Return missing frame numbers between min(frames) and max(frames)
    """
    if not frames:
        return []
    lo, hi = frames[0], frames[-1]
    have = set(frames)
    missing = [f for f in range(lo, hi + 1) if f not in have]
    return missing

def iter_shot_render_dirs(shows_root: Path) -> Iterable[tuple[str, str, Path]]:
    """
    Yield (show_name, shot_name, render_dir) for: shows_root/<show>/shots/renders
    """
    if not shows_root.exists():
        return
    for show_dir in sorted([p for p in shows_root.iterdir() if p.is_dir()]):
        shots_dir = show_dir / "shots"

        if not shots_dir.exists():
            continue
        
        for shot_dir in sorted([p for p in shots_dir.iterdir() if p.is_dir()]):
            render_dir = shot_dir / "renders"
            if render_dir.exists() and render_dir.is_dir():
                yield show_dir.name, shot_dir.name, render_dir

def validate_renders(
        shows_root: Path,
        *,
        frame_prefix: str = "frame_",
        frame_padding: int = 4,
        frame_ext: str = ".exr",
) -> list[ShotValidationResult]:
    """
    Scan all shot render dirs and report missing frames for each shot
    """
    frame_re = _build_frame_regex(frame_prefix, frame_padding, frame_ext)
    results: list[ShotValidationResult] = []
    for show, shot, render_dir in iter_shot_render_dirs(shows_root):
        frames = _collect_frame_numbers(render_dir, frame_re)
        missing = _compute_missing(frames)
        results.append(
            ShotValidationResult(
                show=show,
                shot=shot,
                render_dir=render_dir,
                frames_found=frames,
                missing_frames=missing
            )
        )
    return results