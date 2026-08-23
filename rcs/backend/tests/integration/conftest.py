"""Integration test config: ensure rcs_backend is importable."""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent  # rcs/backend/
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
