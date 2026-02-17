# Architecture

## Overview
The toolkit is a config-driven CLI that scans a show/shot filesystem layout and produces reports.
It supports both human-readable output and JSON for integration.

## Modules
- `validation.py`: finds missing frames in render sequences
- `monitoring.py`: computes disk usage per shot renders directory
- `publishing.py`: combines validation + disk usage into a publish record
- `tracking/`: adapter-style interface + JSON backend (`JsonTracker`)
- `logging_utils.py`: file logging setup

## Integration points
- Config-driven paths + naming rules (`toolkit.yaml`)
- JSON output for parsing by other tools (paths are POSIX-style for portability)
- Tracking adapter interface enables swapping JSON backend for a real tracking system later

## Example dataset
The repo includes a small example dataset under `examples/`:
- `shot010`: missing frame 0003 (validation warning)
- `shot020`: clean sequence 0001-0003 (validation OK)
- `shot030`: larger frames to trigger disk warnings when using `toolkit_demo.yaml` (`disk_warning_mb: 0.03`)

## Safety model
- No destructive operations on render outputs
- `publish` writes metadata only (default: `data/tracking_db.json`)