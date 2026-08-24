"""RCS Backend v2.2 — unified extension layer."""
from rcs.main import create_app
from rcs.config import Settings

__version__ = "0.1.0"
__all__ = ["create_app", "Settings", "__version__"]
