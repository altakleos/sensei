# Ensure bare sibling imports (e.g. ``from _iso import parse_iso``) resolve
# when scripts are imported as a package (``from sensei.engine.scripts.X …``).
# When scripts run standalone via run.sh, PYTHONPATH provides the same effect.
import sys as _sys
from pathlib import Path as _Path

_scripts_dir = str(_Path(__file__).resolve().parent)
if _scripts_dir not in _sys.path:
    _sys.path.insert(0, _scripts_dir)
