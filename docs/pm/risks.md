# Risks and mitigations

## Risk: Breaking production data
Mitigation:
- read-only design
- no deletes/moves
- publish records metadata only

## Risk: Environment differences (paths, OS)
Mitigation:
- config-driven paths (toolkit.yaml)
- Pathlib usage
- CLI overrides

## Risk: External service integration complexity
Mitigation:
- tracking adapter design
- local JSON backend for portability
- defer real Flow/ShotGrid API integration