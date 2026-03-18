from __future__ import annotations

import logging
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ExecResult:
    returncode: int
    stdout: str
    stderr: str
    success: bool = False

    def __post_init__(self):
        object.__setattr__(self, 'success', self.returncode == 0)


class ExecError(RuntimeError):
    def __init__(self, message: str, *, result: ExecResult | None = None) -> None:
        super().__init__(message)
        self.result = result


def _format_cmd(cmd: Sequence[str] | str) -> str:
    if isinstance(cmd, str):
        return cmd
    return " ".join(shlex.quote(p) for p in cmd)


def run(
    cmd: Sequence[str] | str,
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
    verbose: bool = False,
    check: bool = True,
    default_cwd: Path | None = None,
) -> ExecResult:
    """
    Execute a subprocess command.

    Stub-friendly contract: always returns an ExecResult; raises ExecError on failure if check=True.
    """
    rendered = _format_cmd(cmd)
    if dry_run:
        return ExecResult(returncode=0, stdout=f"[DRY-RUN] {rendered}\n", stderr="")

    if verbose:
        logging.info(f"[exec] {rendered}")

    actual_cwd = cwd if cwd is not None else default_cwd

    completed = subprocess.run(
        cmd,
        cwd=str(actual_cwd) if actual_cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        shell=isinstance(cmd, str),
    )
    result = ExecResult(
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if check and result.returncode != 0:
        raise ExecError(f"Command failed ({result.returncode}): {rendered}", result=result)
    return result
