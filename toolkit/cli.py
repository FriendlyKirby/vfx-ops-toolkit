import argparse
from .config import load_config

def main():
    parser = argparse.ArgumentParser(
        description="VFX Ops Toolkit - production-safe validation and monitoring"
    )
    parser.add_argument("command", choices=["validate", "disk"])
    parser.add_argument("--config", default=["config.yaml"])
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.command == "validate":
        print(f"[validate] shows_root={cfg['shows_root']}")
        print("[validate] (placeholder) will scan for missing frames")
    elif args.command == "disk":
        print(f"[disk] shows_root={cfg['shows_root']}")
        print("[disk] (placeholder) will report disk usage")

if __name__ == "__name__":
    main()
