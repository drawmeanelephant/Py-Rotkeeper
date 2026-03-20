from __future__ import annotations
import importlib
import pkgutil
from pathlib import Path

def get_commands():
    """
    Dynamically discover all lib modules that expose add_parser().
    """
    package_dir = Path(__file__).parent
    commands = []
    for finder, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        module = importlib.import_module(f".{module_name}", package=__name__)
        if hasattr(module, "add_parser"):
            commands.append((module_name, module.add_parser))
    return commands
