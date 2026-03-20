from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunContext:
    dry_run: bool
    verbose: bool
    log_file: Path | None
    config: object | None = None
    # sitemap-pipeline stage flags
    index_only: bool = False
    metadata_only: bool = False
    write_only: bool = False
