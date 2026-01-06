from pathlib import Path
import yaml

def load_config(path=None) -> dict:
    # If argparse gives 1-item list (nargs=1) or append list -> normalize it
    if isinstance(path, list):
        path = path[-1] if path else None

    if path is None:
        candidate = Path.cwd() / "toolkit.yaml"
        if not candidate.exists():
            return {}
        p = candidate
    else:
        p = Path(path)

    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config must be a mapping (dict). Got: {type(data).__name__}")

    return data
