"""Root conftest: add rcs/backend/ to sys.path."""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "_rcs"))
sys.path.insert(0, str(_ROOT / "_shared"))
