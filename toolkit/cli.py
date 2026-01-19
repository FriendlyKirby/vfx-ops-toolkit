import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import load_config
from .logging_utils import setup_logging
from .monitoring import bytes_to_mb, disk_usage_by_shot, format_bytes
from .publishing import PublishError, publish_shot
from .tracking.factory import make_tracker
from .validation import validate_renders


def main() -> int:
    """
    CLI entrypoint. Returns a process exit code (0 ok, 1 validation issues).
    """
    parser = argparse.ArgumentParser(
        prog="toolkit",
        description="VFX Ops Toolkit - production-safe validation and monitoring"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    validate_p = sub.add_parser("validate", help="Scan renders and report missing frames")
    disk_p = sub.add_parser("disk", help="Report disk usage by show/shot")
    publish_p = sub.add_parser("publish", help="Record publish metadata")
    list_p = sub.add_parser("list-publishes", help="List publish records from tracking backend")

    publish_p.add_argument("--show", required=True, help="Show name (e.g. demo_show)")
    publish_p.add_argument("--shot", required=True, help="Shot name (e.g. shot010)")
    publish_p.add_argument("--version", default="v001", help="Publish version (default: v001)")
    publish_p.add_argument("--note", default="", help="Optional publish note")

    list_p.add_argument("--show", default=None, help="Filter by show")
    list_p.add_argument("--shot", default=None, help="Filter by shot")
    list_p.add_argument("--limit", type=int, default=50, help="Max records to display (default: 50)")

    for p in (validate_p, disk_p, publish_p, list_p):
        p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
        p.add_argument("--log-dir", default=None, help="Directory for log files (default: ./logs)")
        p.add_argument("--config", default=None, help="Path to toolkit.yaml (default: ./toolkit.yaml)")
        p.add_argument("--shows-root", default=None, help="Override shows_root from config")

    args = parser.parse_args()

    cfg = load_config(args.config)

    # Resolve settings: CLI overrides config, then fall back to defaults
    shows_root = Path(args.shows_root or cfg.get("shows_root", "examples/shows"))

    log_dir_value = args.log_dir or cfg.get("log_dir", "logs")
    log_dir = Path(log_dir_value)

    logger = setup_logging(log_dir)
    logger.info("command=%s shows_root=%s", args.command, shows_root)

    use_json = bool(args.json)

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

        if use_json:
            payload = {
                "tool": "vfx-ops-toolkit",
                "command": "validate",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "shows_root": str(shows_root),
                "results": [
                    {
                        "show": r.show,
                        "shot": r.shot,
                        "render_dir": str(r.render_dir),
                        "frames_found": r.frames_found,
                        "missing_frames": r.missing_frames
                    }
                    for r in results
                ]
            }
            print(json.dumps(payload, indent=2))
            had_missing = any(r.missing_frames for r in results)
            return 1 if had_missing else 0

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
                logger.warning("missing_frames show=%s shot=%s missing=%s", r.show, r.shot, r.missing_frames)
            else:
                print("    OK (no missing frames)")

        return 1 if had_missing else 0

    if args.command == "disk":
        results = disk_usage_by_shot(shows_root)

        thresholds = cfg.get("thresholds", {}) if isinstance(cfg.get("thresholds", {}), dict) else {}
        try:
            warn_mb = float(thresholds.get("disk_warning_mb", 0))
        except (TypeError, ValueError):
            warn_mb = 0.0

        if use_json:
            payload = {
                "tool": "vfx-ops-toolkit",
                "command": "disk",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "shows_root": str(shows_root),
                "results": [
                    {
                        "show": r.show,
                        "shot": r.shot,
                        "render_dir": str(r.render_dir),
                        "total_bytes": r.total_bytes,
                        "file_count": r.file_count,
                        "total_mb": round(bytes_to_mb(r.total_bytes), 3),
                        "warning": (warn_mb > 0 and bytes_to_mb(r.total_bytes) >= warn_mb)
                    }
                    for r in results
                ]
            }
            print(json.dumps(payload, indent=2))
            return 0

        print(f"Disk usage under: {shows_root}")
        if not results:
            print("No shots found.")
            return 0

        results.sort(key=lambda r: (r.show, r.shot))
        current_show = None

        for r in results:
            if r.show != current_show:
                current_show = r.show
                print(f"\nShow: {r.show}")

            mb = bytes_to_mb(r.total_bytes)
            warn = (warn_mb > 0 and mb >= warn_mb)

            line = f"  Shot: {r.shot}  renders={format_bytes(r.total_bytes)} ({r.file_count} files)"
            if warn:
                line += f"  [WARN >= {warn_mb:.0f} MB]"
                logger.warning("disk_warning show=%s shot=%s mb=%.3f threshold=%.3f", r.show, r.shot, mb, warn_mb)

            print(line)

        logger.info("disk_scan_complete shots=%d", len(results))
        return 0

    if args.command == "publish":
        try:
            tracker = make_tracker(cfg)
        except ValueError as e:
            print(str(e))
            return 2

        try:
            result = publish_shot(
                shows_root=shows_root,
                show=args.show,
                shot=args.shot,
                version=args.version,
                note=args.note,
                tracker=tracker,
                frame_prefix=frame_prefix,
                frame_padding=frame_padding,
                frame_ext=frame_ext,
            )
        except PublishError as e:
            logger.error("publish_failed %s", e)
            print(f"ERROR: {e}")
            return 2

        logger.info(
            "publish show=%s shot=%s version=%s status=%s",
            result.record.show,
            result.record.shot,
            result.record.version,
            result.record.status,
        )

        if use_json:
            payload = {
                "tool": "vfx-ops-toolkit",
                "command": "publish",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "record": {
                    "show": result.record.show,
                    "shot": result.record.shot,
                    "version": result.record.version,
                    "status": result.record.status,
                    "note": result.record.note,
                    "timestamp_utc": result.record.timestamp_utc,
                    "frames_found": result.record.frames_found,
                    "missing_frames": result.record.missing_frames,
                    "total_bytes": result.record.total_bytes,
                    "file_count": result.record.file_count,
                },
            }
            print(json.dumps(payload, indent=2))
            return 0

        print("Publish recorded:")
        print(f"  Show: {result.record.show}")
        print(f"  Shot: {result.record.shot}")
        print(f"  Version: {result.record.version}")
        print(f"  Status: {result.record.status}")
        if result.record.missing_frames:
            missing_str = ", ".join(f"{f:0{frame_padding}d}" for f in result.record.missing_frames)
            print(f"  Missing frames: {missing_str}")
        print(f"  Renders size: {format_bytes(result.record.total_bytes)} ({result.record.file_count} files)")
        if result.record.note:
            print(f"  Note: {result.record.note}")

        return 0

    if args.command == "list-publishes":
        try:
            tracker = make_tracker(cfg)
        except ValueError as e:
            print(str(e))
            return 2

        records = tracker.list_publishes(show=args.show, shot=args.shot)
        records = records[: max(0, args.limit)]

        if use_json:
            payload = {
                "tool": "vfx-ops-toolkit",
                "command": "list-publishes",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "filters": {"show": args.show, "shot": args.shot, "limit": args.limit},
                "count": len(records),
                "records": [
                    {
                        "show": r.show,
                        "shot": r.shot,
                        "version": r.version,
                        "status": r.status,
                        "note": r.note,
                        "timestamp_utc": r.timestamp_utc,
                        "frames_found": r.frames_found,
                        "missing_frames": r.missing_frames,
                        "total_bytes": r.total_bytes,
                        "file_count": r.file_count,
                    }
                    for r in records
                ],
            }
            print(json.dumps(payload, indent=2))
            return 0

        if not records:
            print("No publish records found.")
            return 0

        print("Publish records:")
        for r in records:
            line = f"- {r.timestamp_utc}  {r.show}/{r.shot}  {r.version}  status={r.status}"
            if r.note:
                line += f"  note={r.note}"
            print(line)

        return 0

    return 0


def run() -> None:
    raise SystemExit(main())
