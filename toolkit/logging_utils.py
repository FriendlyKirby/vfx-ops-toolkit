from __future__ import annotations
import logging
from  pathlib import Path

def setup_logging(log_dir: Path, level: int = logging.INFO) -> logging.Logger:
    """
    Configure a file logger for the toolkit; returns a logger instance
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "toolkit.log"

    logger = logging.getLogger("toolkit")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_path) for h in logger.handlers):
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(level)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger