from pathlib import Path
import pytest

from toolkit.config import load_config


def test_load_config_returns_empty_when_no_default_file(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    cfg = load_config(None)
    assert cfg == {}


def test_load_config_reads_toolkit_yaml_from_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    (tmp_path / "toolkit.yaml").write_text(
        "shows_root: examples/shows\nnaming:\n  frame_padding: 4\n",
        encoding="utf-8",
    )

    cfg = load_config(None)
    assert cfg["shows_root"] == "examples/shows"
    assert cfg["naming"]["frame_padding"] == 4


def test_load_config_reads_explicit_path(tmp_path: Path):
    cfg_path = tmp_path / "myconfig.yaml"
    cfg_path.write_text("shows_root: X\n", encoding="utf-8")

    cfg = load_config(str(cfg_path))
    assert cfg["shows_root"] == "X"


def test_load_config_raises_if_yaml_not_a_mapping(tmp_path: Path):
    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text("- a\n- list\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(str(cfg_path))


def test_load_config_accepts_list_arg_and_uses_last(tmp_path: Path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("shows_root: A\n", encoding="utf-8")
    b.write_text("shows_root: B\n", encoding="utf-8")

    cfg = load_config([str(a), str(b)])
    assert cfg["shows_root"] == "B"
