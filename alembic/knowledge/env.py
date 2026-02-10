# This file re-exports the shared env.py.
# Alembic uses script_location to find env.py, so each sub-directory
# needs its own env.py that delegates to the shared one.
import importlib
import os
import sys

# Ensure parent alembic/ dir is importable
_alembic_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _alembic_root not in sys.path:
    sys.path.insert(0, _alembic_root)

# Import and execute the shared env module
_shared_env = os.path.join(_alembic_root, "env.py")
spec = importlib.util.spec_from_file_location("alembic_shared_env", _shared_env)
_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(_mod)  # type: ignore[union-attr]
