from pathlib import Path
from toolkit.logging_utils import setup_logging

def test_setup_logging_creates_log_file(tmp_path: Path):
    logger = setup_logging(tmp_path)
    logger.info("hello")

    log_file = tmp_path / "toolkit.log"
    assert log_file.exists()
    text = log_file.read_text(encoding="utf-8")