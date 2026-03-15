from __future__ import annotations

import re
import shutil
from dataclasses import dataclass

from .exec import run


class MissingDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class PandocInfo:
    path: str
    version: str | None


def require_bins(*names: str) -> None:
    missing = [n for n in names if shutil.which(n) is None]
    if missing:
        raise MissingDependencyError(f"Missing required dependencies: {', '.join(missing)}")


def get_pandoc_info() -> PandocInfo:
    require_bins("pandoc")
    pandoc_path = shutil.which("pandoc")
    assert pandoc_path is not None

    version = None
    try:
        res = run(["pandoc", "--version"], check=False)
        first = (res.stdout.splitlines() or [""])[0]
        m = re.search(r"\b(\d+\.\d+(?:\.\d+)?)\b", first)
        version = m.group(1) if m else None
    except Exception:
        version = None

    return PandocInfo(path=pandoc_path, version=version)


def try_import_pypandoc() -> bool:
    try:
        import pypandoc  # noqa: F401
    except Exception:
        return False
    return True

