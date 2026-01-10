# vfx-ops-toolkit

A Python command-line toolkit that simulates production-safe studio utilities for validating render outputs and monitoring storage usage in a VFX-style show/shot folder structure.

**Designed to operate independently of any single DCC application and can be integrated into Maya, Houdini, or Nuke pipelines via simple hooks or publish callbacks.**

## Who this is for
This toolkit is intentionally scoped to reflect day-to-day utilities used by:
- **Technical Assistants (TA):** validation and clear issue reporting
- **Production / Pipeline Engineers:** maintainable tooling and integration-ready design
- **Studio IT / Ops:** safe-by-default automation and reporting
- **Studio Talent / Training Support:** scripting + documentation for enabling teams
- **Technology Project Managers:** milestones and lightweight project artifacts (see `/docs/pm/`)

## Features
**Implemented**
- Runnable module entrypoint: `python -m toolkit ...`
- Missing-frame detection for image sequences (e.g., `frame_0001.exr`)
- Disk usage reporting by show/shot (total size + file count)
- Config-driven naming rules and show root via `toolkit.yaml` (PyYAML)
- Disk warning thresholds via `toolkit.yaml` (e.g., `thresholds.disk_warning_mb`)
- File logging to `logs/toolkit.log` (configurable via `--log-dir` or `log_dir` in YAML)
- Optional machine-readable JSON output via `--json`
- Example “studio-like” directory structure under `examples/`

**Planned**
- Publish simulation + tracking adapter (integration-ready design)
- CI workflow + packaging polish (pyproject + editable installs)
- Documentation polish + expanded examples

## Quick start
```bash
pip install -r requirements.txt
python -m toolkit validate
python -m toolkit disk
```

## Commands
All commands read settings from `toolkit.yaml` by default (or `--config <path>` if provided). You can also override the scanned root with `--shows-root <path>`.

> Note: flags are provided *after* the command (e.g., `python -m toolkit validate --json`).

### `validate`
Scans the configured show/shot structure and reports missing frames in image sequences.

```bash
python -m toolkit validate
```

Example output (with a gap at 0003):
```text
Show: demo_show
  Shot: shot010
    Missing frames: 0003
```

Example output (no gaps):
```text
Show: demo_show
  Shot: shot010
    OK (no missing frames).
```

Machine-readable output:
```bash
python -m toolkit validate --json
```

### `disk`
Reports disk usage for each shot render directory (total size + file count). If a threshold is configured, shots meeting/exceeding the warning threshold are annotated.

```bash
python -m toolkit disk
```

Example output:
```text
Disk usage under: examples/shows

Show: demo_show
  Shot: shot010  renders=0 B (3 files)
```

Example output (with threshold warnings enabled):
```text
Show: demo_show
  Shot: shot010  renders=512.0 MB (239 files)  [WARN >= 500 MB]
```

Machine-readable output:
```bash
python -m toolkit disk --json
```

### `publish` (placeholder)
Currently prints the configured `shows_root` and a placeholder message.

```bash
python -m toolkit publish
```

Example output:
```text
[publish] shows_root=examples/shows
[publish] (placeholder) will record publish metadata (no file moves/deletes)
```

## Configuration
The toolkit reads `toolkit.yaml`:

```yaml
shows_root: "examples/shows"

naming:
  frame_prefix: "frame_"
  frame_padding: 4
  frame_ext: ".exr"

thresholds:
  disk_warning_mb: 500
```

Run with an explicit config path:
```bash
python -m toolkit validate --config toolkit.yaml
```

Override the root without editing YAML:
```bash
python -m toolkit validate --shows-root examples/shows
```

Write logs to a custom directory:
```bash
python -m toolkit validate --log-dir logs
```

## Safety
The toolkit is **read-only by default**:
- No files are deleted, moved, or modified
- Commands scan and report only
- Intended to be safe to run on shared storage

## Integration-ready tracking
In real studios, publish events are often tracked in a production system (e.g., Autodesk Flow Production Tracking).
This project is designed so tracking can be added without entangling core logic:

- Core validation/analysis should not depend on an external service
- A small tracking adapter interface can support different backends
- A local simulated tracker (e.g., JSON file) keeps the project runnable anywhere (including CI)

## Repository layout
```text
toolkit/
  __main__.py         # module entrypoint (python -m toolkit)
  cli.py              # CLI parsing + command dispatch
  config.py           # YAML config loader
  validation.py       # render validation (missing frames)
  monitoring.py       # disk usage reporting + formatting helpers
  logging_utils.py    # file logging setup
examples/
  shows/demo_show/shots/shot010/renders/
    frame_0001.exr
    frame_0002.exr
    frame_0004.exr   # (0003 missing on purpose for validation)
docs/
  pm/
  training/
logs/                 # run logs (toolkit.log)
toolkit.yaml
requirements.txt
requirements-dev.txt
tests/
README.md
LICENSE
```

## Status / roadmap
- [x] Foundation: package entrypoint + config-driven CLI scaffold
- [x] Implement `validate`: scan image sequences and report missing frames
- [x] Implement `disk`: compute disk usage by show/shot and compare to thresholds
- [x] Add logging + structured output (human + machine readable JSON)
- [x] Add unit tests for core modules
- [ ] Add publish simulation + tracking adapter interface
- [ ] Packaging polish (pyproject + editable install) + CLI subprocess tests
- [ ] Documentation polish + expanded examples

## Non-goals
- This is not a renderer, render farm scheduler, or DCC plugin.
- The focus is on production-safe validation and operational tooling around file outputs.
