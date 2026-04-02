from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Central configuration singleton for Rotkeeper.

    Holds paths, flags, scenario info, and dependencies.
    Scripts query this instead of hardcoding anything.
    """

    def __init__(self) -> None:
        self.ROOTDIR: Path = Path(__file__).resolve().parent.parent.parent
        self.BASEDIR: Path = Path.cwd()
        self.BONES: Path = self.BASEDIR / "bones"
        self.HOME: Path = self.BASEDIR / "home"
        self.CONTENT_DIR: Path = self.HOME
        self.OUTPUTDIR: Path = self.BASEDIR / "output"
        self.baseurl: str = ""
        self.defaulttemplate: str | None = None
        self.SCENARIO: str = "default"
        self.DEPENDENCIES: dict = {
            "pandoc": {"check": ["pandoc", "--version"], "required": True},
            "sass":   {"check": ["sass",   "--version"], "required": False},
            "node":   {"check": ["node",   "--version"], "required": False},
        }
        user_config_path = self.BONES / "config" / "user-config.yaml"
        if user_config_path.exists():
            try:
                with open(user_config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                self.apply(data)
            except yaml.YAMLError as e:
                logger.error("user-config.yaml is malformed and will be ignored: %s", e)

    # ------------------------------------------------------------------
    # Computed / optional properties

    @property
    def REPORTS_DIR(self) -> Path:
        return getattr(self, "_reportsdir", self.BONES / "reports")

    @property
    def GENERATEDCONTENT_DIR(self) -> Path:
        return getattr(self, "_generatedcontentdir", self.CONTENT_DIR / "generated")

    @property
    def GENERATEINDEXES(self) -> bool:
        return getattr(self, "_generateindexes", True)

    # ROOTDIR alias for any legacy references
    @property
    def ROOT_DIR(self) -> Path:
        return self.ROOTDIR

    def apply(self, data: dict) -> None:
        """Apply a config dict, overriding current values."""
        if not data:
            return
        known = {
            "HOME", "CONTENT_DIR", "OUTPUTDIR", "defaulttemplate", "SCENARIO",
            "REPORTS_DIR", "GENERATEDCONTENT_DIR", "baseurl", "generateindexes",
        }
        unknown = set(data.keys()) - known
        if unknown:
            logger.warning("Unrecognized keys in config (typo?): %s", sorted(unknown))
        if "HOME" in data:
            self.HOME = (self.BASEDIR / data["HOME"]).resolve()
        if "CONTENT_DIR" in data:
            self.CONTENT_DIR = (self.BASEDIR / data["CONTENT_DIR"]).resolve()
        if "OUTPUTDIR" in data:
            self.OUTPUTDIR = (self.BASEDIR / data["OUTPUTDIR"]).resolve()
        if "defaulttemplate" in data:
            self.defaulttemplate = data["defaulttemplate"]
        if "SCENARIO" in data:
            self.SCENARIO = data["SCENARIO"]
        if "REPORTS_DIR" in data:
            self._reportsdir = (self.BASEDIR / data["REPORTS_DIR"]).resolve()
        if "GENERATEDCONTENT_DIR" in data:
            self._generatedcontentdir = (self.BASEDIR / data["GENERATEDCONTENT_DIR"]).resolve()
        if "baseurl" in data:
            self.baseurl = data["baseurl"]
        if "generateindexes" in data:
            self._generateindexes = bool(data["generateindexes"])

    def load(self, path: Path) -> None:
        """Load configuration overrides from a YAML file.

        When a config file is explicitly loaded, BASEDIR is rebound to the
        project root inferred from the config file's location. This supports
        running rotkeeper from outside the project directory, e.g.:
            rotkeeper --config sites/site-a/bones/config/user-config.yaml render

        Assumes the config file lives at <project-root>/bones/config/*.yaml,
        so project root = config_file.parent.parent.parent.
        If the file is not in that structure, BASEDIR stays as Path.cwd().
        """
        if not path.exists():
            logger.warning("Config path not found %s, running with defaults", path)
            return
        inferred_root = path.resolve().parent.parent.parent
        if inferred_root.exists():
            self.BASEDIR = inferred_root
            self.BONES = self.BASEDIR / "bones"
            self.HOME = self.BASEDIR / "home"
            self.CONTENT_DIR = self.HOME
            self.OUTPUTDIR = self.BASEDIR / "output"
            logger.debug("Config BASEDIR rebound to %s", self.BASEDIR)
        else:
            logger.warning(
                "Could not infer project root from config path %s "
                "(expected root/bones/config/file.yaml layout). "
                "Keeping BASEDIR=%s",
                path, self.BASEDIR,
            )
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error("Invalid YAML in config %s: %s, running with defaults", path, e)
            return
        self.apply(data)

    def output_path(self, filename: str) -> Path:
        """Compute output path for a given file under the current scenario."""
        return self.OUTPUTDIR / self.SCENARIO / filename


CONFIG = Config()
