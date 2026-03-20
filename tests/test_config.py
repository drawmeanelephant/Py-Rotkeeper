import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
import yaml

from rc.config import Config


MINIMAL_YAML = yaml.dump({
    "HOME": "custom_home",
    "CONTENT_DIR": "custom_content",
    "OUTPUT_DIR": "custom_output",
    "default_template": "base.html",
})


class TestConfigDefaults:
    def test_default_home(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.HOME == tmp_path / "home"

    def test_default_content_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.CONTENT_DIR == tmp_path / "home" / "content"

    def test_default_output_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.OUTPUT_DIR == tmp_path / "home" / "output"

    def test_default_template_is_none(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.default_template is None

    def test_default_flags(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.DRY_RUN is False
        assert cfg.DEBUG is False

    def test_default_scenario(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        assert cfg.SCENARIO == "default"


class TestConfigUserYaml:
    def _write_user_config(self, tmp_path,  dict):
        config_dir = tmp_path / "bones" / "config"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "user-config.yaml"
        config_file.write_text(yaml.dump(data), encoding="utf-8")

    def test_home_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_user_config(tmp_path, {"HOME": "my_home"})
        cfg = Config()
        assert cfg.HOME == tmp_path / "my_home"

    def test_content_dir_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_user_config(tmp_path, {"CONTENT_DIR": "src/content"})
        cfg = Config()
        assert cfg.CONTENT_DIR == tmp_path / "src" / "content"

    def test_output_dir_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_user_config(tmp_path, {"OUTPUT_DIR": "dist"})
        cfg = Config()
        assert cfg.OUTPUT_DIR == tmp_path / "dist"

    def test_default_template_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_user_config(tmp_path, {"default_template": "base.html"})
        cfg = Config()
        assert cfg.default_template == "base.html"

    def test_missing_user_config_is_fine(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()  # no bones/config/user-config.yaml
        assert cfg.HOME == tmp_path / "home"


class TestConfigLoad:
    def test_load_overrides_home(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        load_file = tmp_path / "myconfig.yaml"
        load_file.write_text(yaml.dump({"HOME": "loaded_home"}), encoding="utf-8")
        cfg = Config()
        cfg.load(load_file)
        assert cfg.HOME == tmp_path / "loaded_home"

    def test_load_overrides_template(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        load_file = tmp_path / "myconfig.yaml"
        load_file.write_text(yaml.dump({"default_template": "dark.html"}), encoding="utf-8")
        cfg = Config()
        cfg.load(load_file)
        assert cfg.default_template == "dark.html"

    def test_load_missing_file_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        with pytest.raises(FileNotFoundError):
            cfg.load(tmp_path / "nonexistent.yaml")


class TestOutputPath:
    def test_output_path_default_scenario(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = Config()
        result = cfg.output_path("sitemap.yaml")
        assert result == tmp_path / "home" / "output" / "default" / "sitemap.yaml"
