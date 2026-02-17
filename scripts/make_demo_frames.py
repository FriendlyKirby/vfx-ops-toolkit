from pathlib import Path

SHOT010_RENDERS = Path("examples/shows/demo_show/shots/shot010/renders")
SHOT020_RENDERS = Path("examples/shows/demo_show/shots/shot020/renders")
SHOT030_RENDERS = Path("examples/shows/demo_show/shots/shot030/renders")

def main() -> None:
    SHOT010_RENDERS.mkdir(parents=True, exist_ok=True)
    SHOT020_RENDERS.mkdir(parents=True, exist_ok=True)
    SHOT030_RENDERS.mkdir(parents=True, exist_ok=True)

    # shot010: missing frame 0003
    (SHOT010_RENDERS / "frame_0001.exr").write_bytes(b"x" * 1024)   # 1 KB
    (SHOT010_RENDERS / "frame_0002.exr").write_bytes(b"x" * 2048)   # 2 KB
    (SHOT010_RENDERS / "frame_0004.exr").write_bytes(b"x" * 1024)   # 1 KB

    # shot020: clean sequence (0001-0003)
    (SHOT020_RENDERS / "frame_0001.exr").write_bytes(b"x" * 1024)   # 1 KB
    (SHOT020_RENDERS / "frame_0002.exr").write_bytes(b"x" * 1024)   # 1 KB
    (SHOT020_RENDERS / "frame_0003.exr").write_bytes(b"x" * 1024)   # 1 KB

    # shot030: larger frames to trigger disk warning with toolkit_demo.yaml
    (SHOT030_RENDERS / "frame_0001.exr").write_bytes(b"x" * 12288)  # 12 KB
    (SHOT030_RENDERS / "frame_0002.exr").write_bytes(b"x" * 12288)  # 12 KB
    (SHOT030_RENDERS / "frame_0003.exr").write_bytes(b"x" * 12288)  # 12 KB

    print("Wrote demo frames to:")
    print(f"  {SHOT010_RENDERS}")
    print(f"  {SHOT020_RENDERS}")
    print(f"  {SHOT030_RENDERS}")

if __name__ == "__main__":
    main()