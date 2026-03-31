# rc/rotkeeper/config.py
from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Central configuration singleton for Rotkeeper.

    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self):
        self.ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        self.BASE_DIR = Path.cwd()
        self.BONES    = self.BASE_DIR / "bones"
        self.HOME     = self.BASE_DIR / "home"
        self.CONTENT_DIR = self.HOME
        self.OUTPUT_DIR  = self.BASE_DIR / "output"
        self.base_url    = ""
        self.default_template = None
        self.SCENARIO = "default"
        self.DEPENDENCIES = {
            "pandoc": {"check": ["pandoc", "--version"], "required": True},
            "sass":   {"check": ["sass",   "--version"], "required": False},
            "node":   {"check": ["node",   "--version"], "required": False},
        }

        user_config_path = self.BONES / "config" / "user-config.yaml"
        if user_config_path.exists():
            try:
                with open(user_config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                self._apply(data)
            except yaml.YAMLError as e:
                logger.error(
                    "user-config.yaml is malformed and will be ignored: %s", e
                )

    # ------------------------------------------------------------------
    # Overridable output paths (set via _apply / load)
    # ------------------------------------------------------------------

    @property
    def REPORTS_DIR(self) -> Path:
        return getattr(self, "_reports_dir", self.BONES / "reports")

    @property
    def GENERATED_CONTENT_DIR(self) -> Path:
        return getattr(self, "_generated_content_dir", self.CONTENT_DIR / "generated")

    # ROOTDIR alias for any legacy references
    @property
    def ROOTDIR(self) -> Path:
        return self.ROOT_DIR

    @property
    def GENERATE_INDEXES(self) -> bool:
        return getattr(self, "_generate_indexes", True)

    # ------------------------------------------------------------------

    def _apply(self, data: dict) -> None:
        """Apply a config dict, overriding current values."""
        if not data:
            return

        known = {
            "HOME", "CONTENT_DIR", "OUTPUT_DIR", "default_template",
            "SCENARIO", "REPORTS_DIR", "GENERATED_CONTENT_DIR", "base_url",
            "generate_indexes",          # NEW – controls generated/ folder
        }
        unknown = set(data.keys()) - known
        if unknown:
            logger.warning(
                "Unrecognized keys in config (typo?): %s", sorted(unknown)
            )

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
        if "REPORTS_DIR" in data:
            self._reports_dir = (self.BASE_DIR / data["REPORTS_DIR"]).resolve()
        if "GENERATED_CONTENT_DIR" in data:
            self._generated_content_dir = (
                self.BASE_DIR / data["GENERATED_CONTENT_DIR"]
            ).resolve()
        if "base_url" in data:
            self.base_url = data["base_url"]
        if "generate_indexes" in data:
            self._generate_indexes = bool(data["generate_indexes"])

    def load(self, path: Path) -> None:
        """Load configuration overrides from a YAML file.

        When a config file is explicitly loaded, BASE_DIR is rebound to the
        project root inferred from the config file's location. This supports
        running rotkeeper from outside the project directory, e.g.:

            rotkeeper --config /sites/site-a/bones/config/user-config.yaml render

        Assumes the config file lives at <project_root>/bones/config/*.yaml,
        so project root = config_file.parent.parent.parent.
        If the file is not in that structure, BASE_DIR stays as Path.cwd().
        """
        if not path.exists():
            logger.warning(
                "Config path not found: %s — running with defaults", path
            )
            return

        inferred_root = path.resolve().parent.parent.parent
        if inferred_root.exists():
            self.BASE_DIR = inferred_root
            self.BONES    = self.BASE_DIR / "bones"
            self.HOME     = self.BASE_DIR / "home"
            self.CONTENT_DIR = self.HOME
            self.OUTPUT_DIR  = self.BASE_DIR / "output"
            logger.debug("Config: BASE_DIR rebound to %s", self.BASE_DIR)
        else:
            logger.warning(
                "Could not infer project root from config path %s — "
                "expected <root>/bones/config/<file>.yaml layout. "
                "Keeping BASE_DIR=%s",
                path, self.BASE_DIR,
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(
                "Invalid YAML in config %s: %s — running with defaults", path, e
            )
            return

        self._apply(data)

    # ------------------------------------------------------------------

    def output_path(self, filename: str) -> Path:
        """Compute output path for a given file under the current scenario."""
        return self.OUTPUT_DIR / self.SCENARIO / filename


CONFIG = Config()