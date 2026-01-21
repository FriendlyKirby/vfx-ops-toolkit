# Quickstart (VFX Ops Toolkit)

This toolkit scans a VFX-style show/shot folder structure to:
- detect missing frames in render outputs
- report disk usage per shot
- record and list publish events (metadata only)

## Setup

### Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### (Optional) Install as a command
If you have `pyproject.toml` set up, you can install the toolkit in editable mode so the `toolkit` command is available:
```bash
pip install -e .
```

## Common commands

### Validate renders
```bash
toolkit validate
```
If frames are missing, the exit code is `1`.

### Disk usage
```bash
toolkit disk
```

### Publish a shot (metadata only)
```bash
toolkit publish --show demo_show --shot shot010 --version v001 --note "publish test"
```

### List publish history
```bash
toolkit list-publishes
toolkit list-publishes --show demo_show
toolkit list-publishes --json
```

## JSON mode
Add `--json` to any command to print machine-readable output:
```bash
toolkit validate --json
```

## Logs
Logs are written to `logs/toolkit.log` by default.

Override with:
```bash
toolkit validate --log-dir my_logs
```