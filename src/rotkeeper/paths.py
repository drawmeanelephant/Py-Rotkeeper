from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class RootNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True)
class Paths:
    root_dir: Path

    # Top-level
    output_dir: Path
    tmp_dir: Path
    venv_dir: Path
    tests_dir: Path

    # Home content
    home_dir: Path
    content_dir: Path
    assets_dir: Path
    docs_dir: Path
    help_dir: Path

    # Bones
    bones_dir: Path
    scripts_dir: Path
    config_dir: Path
    logs_dir: Path
    archive_dir: Path
    reports_dir: Path
    templates_dir: Path
    meta_dir: Path

    # Render-related paths
    manifests_dir: Path
    build_dir: Path
    render_templates_dir: Path
    assets_manifest: Path

    @classmethod
    def from_root(cls, root_dir: Path) -> "Paths":
        root_dir = root_dir.resolve()

        output_dir = root_dir / "output"
        tmp_dir = root_dir / "tmp"
        venv_dir = root_dir / "venv"
        tests_dir = root_dir / "tests"

        home_dir = root_dir / "home"
        content_dir = home_dir / "content"
        assets_dir = home_dir / "assets"
        docs_dir = content_dir / "docs"
        help_dir = content_dir / "help"

        bones_dir = root_dir / "bones"
        scripts_dir = bones_dir / "scripts"
        config_dir = bones_dir / "config"
        logs_dir = bones_dir / "logs"
        archive_dir = bones_dir / "archive"
        reports_dir = bones_dir / "reports"
        templates_dir = bones_dir / "templates"
        meta_dir = bones_dir / "meta"

        manifests_dir = root_dir / "manifests"
        build_dir = root_dir / "build"
        render_templates_dir = templates_dir / "render"
        assets_manifest = reports_dir / "assets.yaml"

        return cls(
            root_dir=root_dir,
            output_dir=output_dir,
            tmp_dir=tmp_dir,
            venv_dir=venv_dir,
            tests_dir=tests_dir,
            home_dir=home_dir,
            content_dir=content_dir,
            assets_dir=assets_dir,
            docs_dir=docs_dir,
            help_dir=help_dir,
            bones_dir=bones_dir,
            scripts_dir=scripts_dir,
            config_dir=config_dir,
            logs_dir=logs_dir,
            archive_dir=archive_dir,
            reports_dir=reports_dir,
            templates_dir=templates_dir,
            meta_dir=meta_dir,
            manifests_dir=manifests_dir,
            build_dir=build_dir,
            render_templates_dir=render_templates_dir,
            assets_manifest=assets_manifest,
        )


def _looks_like_tomb_root(root_dir: Path) -> bool:
    # Keep this intentionally permissive; init should be able to create missing dirs.
    bones = root_dir / "bones"
    home = root_dir / "home"
    return bones.exists() or home.exists()


def discover_root(explicit_root: str | Path | None = None) -> Path:
    """
    Resolve the Rotkeeper project root.

    Heuristics:
    - If explicit_root is provided, use it (must exist).
    - Else, if CWD looks like a tomb root, use CWD.
    - Else, if CWD contains a `road-to-bones/` tomb, use that.
    """
    if explicit_root is not None:
        root = Path(explicit_root).expanduser().resolve()
        if not root.exists():
            raise RootNotFoundError(f"Root does not exist: {root}")
        return root

    cwd = Path.cwd().resolve()
    if _looks_like_tomb_root(cwd):
        return cwd

    candidate = cwd / "road-to-bones"
    if candidate.exists() and _looks_like_tomb_root(candidate):
        return candidate.resolve()

    raise RootNotFoundError(
        "Unable to locate Rotkeeper root. Pass --root or run from the tomb directory."
    )
