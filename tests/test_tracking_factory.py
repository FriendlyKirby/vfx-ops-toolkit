from pathlib import Path
import pytest

from toolkit.tracking.factory import make_tracker
from toolkit.tracking.json_tracker import JsonTracker


def test_make_tracker_defaults_to_json_backend(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    t = make_tracker({})
    assert isinstance(t, JsonTracker)


def test_make_tracker_raises_on_unknown_backend():
    with pytest.raises(ValueError):
        make_tracker({"tracking": {"backend": "nope"}})
