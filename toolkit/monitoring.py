from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .validation import iter_shot_render_dirs

@dataclass(frozen=True)
class ShotDiskUsage:
    """Disk usage summary for one shot render directory"""
    show: str
    shot: str
    render_dir: Path
    total_bytes: int
    file_count: int


def _dir_size_bytes(root: Path) -> tuple[int, int]:
    """
    Returns (total_bytes, file_count) for all files under root (recursive)
    """
    total = 0
    count = 0
    if not root.exists():
        return 0, 0
    
    for p in root.rglob("*"):
        if p.is_file():
            count += 1
            try:
                total += p.stat().st_size
            except OSError:
                continue
    return total, count

def disk_usage_by_shot(shows_root: Path) -> list[ShotDiskUsage]:
    """
    Compute disk usage for each shot's renders directory under show_root
    """
    results: list[ShotDiskUsage] = []
    for show, shot, render_dir in iter_shot_render_dirs(shows_root):
        total, count = _dir_size_bytes(render_dir)
        results.append(
            ShotDiskUsage(
                show=show,
                shot=shot,
                render_dir=render_dir,
                total_bytes=total,
                file_count=count
            )
        )
    return results

def bytes_to_mb(num_bytes: int) -> float:
    return num_bytes / (1024 * 1024)

def format_bytes(num_bytes: int) -> str:
    """
    Covert a byte count into a formatted string (e.g. 1536 -> '1.5 KB')
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    unit_i = 0
    while size >= 1024 and unit_i < len(units) - 1:
        size /= 1024
        unit_i += 1
    if unit_i == 0:
        return f"{int(size)} {units[unit_i]}"
    return f"{size:.1f} {units[unit_i]}"