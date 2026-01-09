import argparse
from pathlib import Path

from .config import load_config
from .validation import validate_renders

def main() -> int: # returns an exit code
    parser = argparse.ArgumentParser(
        prog="toolkit",
        description="VFX Ops Toolkit - production-safe validation and monitoring"
    )
    parser.add_argument("--config", default=None, help="Path to toolkit.yaml (default: ./toolkit.yaml)")
    parser.add_argument("--shows-root", default=None, help="Override shows_root from config")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Scan renders and report missing frames")
    sub.add_parser("disk", help="Report disk usage by show/shot (planned)")
    sub.add_parser("publish", help="Record publish metadata (planned)")

    args = parser.parse_args()
    cfg = load_config(args.config)

    # default
    shows_root = Path(args.shows_root or cfg.get("shows_root", "examples/shows"))
    naming = cfg.get("naming", {}) if isinstance(cfg.get("naming", {}), dict) else {}
    frame_prefix = naming.get("frame_prefix", "frame_")
    try:
        frame_padding = int(naming.get("frame_padding", 4))
    except (TypeError, ValueError):
        frame_padding = 4
    frame_ext = naming.get("frame_ext", ".exr")

    if args.command == "validate":
        results = validate_renders(
            shows_root,
            frame_prefix=frame_prefix,
            frame_padding=frame_padding,
            frame_ext=frame_ext
        )

        if not results:
            print(f"No shots found under: {shows_root}")
            return 0
        
        results.sort(key=lambda r: (r.show, r.shot))
        current_show = None
        had_missing = False

        for r in results:
            if r.show != current_show:
                current_show = r.show
                print(f"Show: {r.show}")
            print(f"  Shot: {r.shot}")

            if not r.frames_found:
                print("    No frames found (no matching files)")
                continue

            if r.missing_frames:
                had_missing = True
                missing_str = ", ".join(f"{f:0{frame_padding}d}" for f in r.missing_frames)
                print(f"    Missing frames: {missing_str}")

            else:
                print("    OK (no missing frames)")

        return 1 if had_missing else 0

    if args.command == "disk":
        print(f"[disk] shows_root={shows_root}")
        print("[disk] (placeholder) will report disk usage")
        return 0

    if args.command == "publish":
        print(f"[publish] shows_root={shows_root}")
        print("[publish] (placeholder) will record publish metadata (no file moves/deletes)")
        return 0

    return 0
