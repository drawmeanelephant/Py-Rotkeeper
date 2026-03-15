from pathlib import Path
from rotkeeper.commands.collect_assets import run
from argparse import Namespace

# Setup dummy context
class DummyPaths:
    home_dir = Path.cwd() / "home"          # real content folder
    output_dir = Path.cwd() / "output"      # real output folder
    assets_dir = Path.cwd() / "bones/assets"

class DummyContext:
    dry_run = True  # Toggle: True = dry-run, False = real copy
    paths = DummyPaths()

ctx = DummyContext()

# Wrapper to add per-file visibility and optional real copy
def run_test():
    print("=== Starting collect-assets test ===")
    args = Namespace()

    # Pre-flight checks
    test_dir = ctx.paths.home_dir
    if not test_dir.exists():
        print(f"[ERROR] Test folder not found: {test_dir}")
        return
    md_files = list(test_dir.rglob("*.md"))
    if not md_files:
        print(f"[WARNING] No Markdown files found in {test_dir}")
    else:
        print(f"Found {len(md_files)} Markdown files:")
        for f in md_files:
            print(" ", f)

    import rotkeeper.commands.collect_assets as ca
    import shutil
    original_copy = shutil.copy2

    def verbose_copy(src, dest, *a, **kw):
        print(f"[{'DRY-RUN' if ctx.dry_run else 'COPY'}] {src} -> {dest}")
        if not ctx.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            return original_copy(src, dest, *a, **kw)
        return src

    ca.shutil.copy2 = verbose_copy

    run(args, ctx)
    print("=== Finished collect-assets test ===")

if __name__ == "__main__":
    run_test()