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
- JSON output for parsing by other tools
- Tracking adapter interface enables swapping JSON backend for a real tracking system later

## Safety model
- No destructive operations on render outputs
- `publish` writes metadata only (default: `data/tracking_db.json`)