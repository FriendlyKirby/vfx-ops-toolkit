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
- CLI wiring for `validate` and `disk` *(currently placeholders)*
- YAML config loading via `config.yaml` (PyYAML)
- Example “studio-like” directory structure under `examples/`

**Planned**
- Missing-frame detection for image sequences (e.g., `frame_0001.exr`)
- Disk usage reporting by show/shot with configurable thresholds
- Publish simulation + tracking adapter (integration-ready design)

## Quick start
```bash
pip install -r requirements.txt
python -m toolkit validate
python -m toolkit disk
```

## Commands
All commands read settings from `config.yaml` by default (or `--config <path>` if provided).

### `validate` (placeholder)
Currently prints the configured `shows_root` and a placeholder message.
```bash
python -m toolkit validate
```

Example output:
```text
[validate] shows_root=examples/shows
[validate] (placeholder) will scan for missing frames
```

### `disk` (placeholder)
Currently prints the configured `shows_root` and a placeholder message.
```bash
python -m toolkit disk
```

Example output:
```text
[disk] shows_root=examples/shows
[disk] (placeholder) will report disk usage
```

## Configuration
The toolkit reads `config.yaml`:

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
python -m toolkit validate --config config.yaml
```

## Safety
The toolkit is **read-only by default** and currently prints messages only.
No files are deleted, moved, or modified.

## Integration-ready tracking
In real studios, publish events are often tracked in a production system (e.g., Autodesk Flow Production Tracking).
This project is designed so tracking can be added without entangling core logic:

- Core validation/analysis should not depend on an external service
- A small tracking adapter interface can support different backends
- A local simulated tracker (e.g., JSON file) keeps the project runnable anywhere (including CI)

## Repository layout
```text
toolkit/
  __main__.py      # module entrypoint (python -m toolkit)
  cli.py           # CLI parsing + command dispatch
  config.py        # YAML config loader
examples/
  shows/demo_show/shots/shot010/renders/
    frame_0001.exr
    frame_0002.exr
    frame_0004.exr   # (0003 missing on purpose for validation)
docs/
  pm/
  training/
logs/              # optional run logs (generated later)
config.yaml
requirements.txt
README.md
LICENSE
```

## Status / roadmap
- [x] Foundation: package entrypoint + config-driven CLI scaffold
- [ ] Implement `validate`: scan image sequences and report missing frames
- [ ] Implement `disk`: compute disk usage by show/shot and compare to thresholds
- [ ] Add publish simulation + tracking adapter interface
- [ ] Add logging + structured output (human + machine readable)
- [ ] Add tests + linting + CI workflow
- [ ] Documentation polish + examples

## Non-goals
- This is not a renderer, render farm scheduler, or DCC plugin.
- The focus is on production-safe validation and operational tooling around file outputs.
