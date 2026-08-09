"""Make the shared wire-contract package importable for the RCS test suite.

``robot_contracts`` lives in ``shared/python`` and is not installed. The RCS
tests (especially the MQTT adapter suite) import it directly, so we add the
directory to ``sys.path`` here -- a rootdir conftest is the single, correct
place to do this rather than scattering sys.path hacks across test files.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[1] / "shared" / "python"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))
