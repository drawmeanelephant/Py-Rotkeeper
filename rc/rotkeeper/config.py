# rc/config.py
from pathlib import Path
import yaml


class Config:
    """
    Central configuration singleton for Rotkeeper.
    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self):
        self.ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        self.BASE_DIR = Path.cwd()
        self.BONES = self.BASE_DIR / "bones"

        # Defaults
        self.HOME = self.BASE_DIR / "home"
        self.CONTENT_DIR = self.HOME / "content"
        self.OUTPUT_DIR = self.HOME / "output"
        self.default_template = None
        self.SCENARIO = "default"
        self.DEPENDENCIES = {
            "pandoc": {"check": ["pandoc", "--version"], "required": True},
            "sass":   {"check": ["sass",   "--version"], "required": False},
            "node":   {"check": ["node",   "--version"], "required": False},
        }

        user_config_path = self.BONES / "config" / "user-config.yaml"
        if user_config_path.exists():
            with open(user_config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._apply(data)

    # ------------------------------------------------------------------
    # Derived paths (override-friendly via user-config.yaml)
    # ------------------------------------------------------------------

    @property
    def REPORTS_DIR(self) -> Path:
        return getattr(self, "_reports_dir", self.BONES / "reports")

    @property
    def GENERATED_CONTENT_DIR(self) -> Path:
        return getattr(self, "_generated_content_dir", self.CONTENT_DIR / "generated")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply(self, data: dict) -> None:
        """Apply a config dict, overriding current values."""
        if not data:
            return
        if "HOME" in data:
            self.HOME = (self.BASE_DIR / data["HOME"]).resolve()
        if "CONTENT_DIR" in data:
            self.CONTENT_DIR = (self.BASE_DIR / data["CONTENT_DIR"]).resolve()
        if "OUTPUT_DIR" in data:
            self.OUTPUT_DIR = (self.BASE_DIR / data["OUTPUT_DIR"]).resolve()
        if "default_template" in data:
            self.default_template = data["default_template"]
        if "SCENARIO" in data:
            self.SCENARIO = data["SCENARIO"]
        # Optional path overrides for generated outputs
        if "REPORTS_DIR" in data:
            self._reports_dir = (self.BASE_DIR / data["REPORTS_DIR"]).resolve()
        if "GENERATED_CONTENT_DIR" in data:
            self._generated_content_dir = (self.BASE_DIR / data["GENERATED_CONTENT_DIR"]).resolve()

    def load(self, path: Path) -> None:
        """Load configuration overrides from a YAML file."""
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self._apply(data)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def output_path(self, filename: str) -> Path:
        """Compute output path for a given file under the current scenario."""
        return self.OUTPUT_DIR / self.SCENARIO / filename


CONFIG = Config()
