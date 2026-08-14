"""Make the shared wire-contract package importable for the RCS test suite.

``robot_contracts`` lives in ``shared/python`` and is not installed. The RCS
tests (especially the MQTT adapter suite) import it directly, so we add the
directory to ``sys.path`` here -- a rootdir conftest is the single, correct
place to do this rather than scattering sys.path hacks across test files.

Also add the repo root so ``import rcs`` resolves to the inner ``rcs/rcs/``
package on its own (the implicit namespace package layout the project ships).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SHARED = _REPO_ROOT / "shared" / "python"
for _p in (str(_REPO_ROOT), str(_SHARED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
