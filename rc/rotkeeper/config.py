# rc/rotkeeper/config.py
from pathlib import Path
import yaml

class Config:
    """
    Central configuration singleton for Rotkeeper.
    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self):
        # Project root is the folder containing rc/
        self.ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        self.BASE_DIR = Path.cwd()
        self.BONES = self.BASE_DIR / "bones"
        # Path to user config file
        user_config_path = self.BONES / "config" / "user-config.yaml"
        config_data = None
        if user_config_path.exists():
            with open(user_config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        # Set defaults
        self.HOME = self.BASE_DIR / "home"
        self.CONTENT_DIR = self.HOME / "content"
        self.OUTPUT_DIR = self.HOME / "output"
        self.default_template = None
        # Override from config if available
        if config_data:
            if "HOME" in config_data:
                self.HOME = (self.BASE_DIR / config_data["HOME"]).resolve()
            if "CONTENT_DIR" in config_data:
                self.CONTENT_DIR = (self.BASE_DIR / config_data["CONTENT_DIR"]).resolve()
            if "OUTPUT_DIR" in config_data:
                self.OUTPUT_DIR = (self.BASE_DIR / config_data["OUTPUT_DIR"]).resolve()
            if "default_template" in config_data:
                self.default_template = config_data["default_template"]

    # Flags
    DRY_RUN: bool = False
    DEBUG: bool = False

    # Scenario / sample content
    SCENARIO: str = "default"

    # Dependency registry (example)
    DEPENDENCIES = {
        "pandoc": {"check": ["pandoc", "--version"], "required": True},
        "sass": {"check": ["sass", "--version"], "required": False},
        "node": {"check": ["node", "--version"], "required": False},
    }

    # Utility methods
    def output_path(self, filename: str) -> Path:
        """Compute output path for a given file."""
        return self.OUTPUT_DIR / self.SCENARIO / filename

# Single shared instance
CONFIG = Config()