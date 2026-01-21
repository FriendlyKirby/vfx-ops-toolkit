from pathlib import Path

RENDER_DIR = Path("examples/shows/demo_show/shots/shot010/renders")

def main() -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    (RENDER_DIR / "frame_0001.exr").write_bytes(b"x" * 1024)   # 1 KB
    (RENDER_DIR / "frame_0002.exr").write_bytes(b"x" * 2048)   # 2 KB
    (RENDER_DIR / "frame_0004.exr").write_bytes(b"x" * 1024)   # 1 KB
    print(f"Wrote demo frames to {RENDER_DIR}")

if __name__ == "__main__":
    main()