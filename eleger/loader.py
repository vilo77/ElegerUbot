"""
Dynamic module loader for ElegerUbot.
Scans modules/ directory and imports all plugin files.
"""

import importlib
import logging
import traceback
from pathlib import Path

LOGS = logging.getLogger("eleger.loader")


def load_all_modules(base_dir: Path) -> tuple[list[str], list[str]]:
    """
    Recursively scan `modules/` under `base_dir`, import every .py file.
    Returns (success_list, failed_list).
    """
    modules_dir = base_dir / "modules"
    if not modules_dir.exists():
        LOGS.warning(f"Modules directory not found: {modules_dir}")
        return [], []

    success: list[str] = []
    failed: list[str] = []

    py_files = sorted(modules_dir.rglob("*.py"))
    for path in py_files:
        if path.name.startswith("_"):
            continue  # skip __init__.py, __pycache__, etc.

        # Build dotted module name: e.g. modules.core.alive
        rel = path.relative_to(base_dir)
        module_name = ".".join(rel.with_suffix("").parts)

        try:
            importlib.import_module(module_name)
            success.append(module_name)
            LOGS.debug(f"  ✓ Loaded: {module_name}")
        except Exception:
            failed.append(module_name)
            LOGS.error(f"  ✗ Failed to load: {module_name}")
            LOGS.error(traceback.format_exc())

    return success, failed
