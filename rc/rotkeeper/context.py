from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .paths import Paths


@dataclass(frozen=True)
class RunContext:
    paths: Paths
    dry_run: bool
    verbose: bool
    log_file: Path | None
    config: object | None = None

