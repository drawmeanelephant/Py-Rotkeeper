# rc/rotkeeper/config.py
from pathlib import Path

class Config:
    """
    Central configuration singleton for Rotkeeper.
    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self):
        self.BASE_DIR = Path.cwd()
        self.HOME = self.BASE_DIR / "home"
        self.BONES = self.BASE_DIR / "bones"
        self.CONTENT_DIR = self.HOME / "content"
        self.OUTPUT_DIR = self.HOME / "output"

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