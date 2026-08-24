"""Motion planning primitives (FK / IK / Trajectory / Interpolator)."""
from .fk import fk
from .ik import ik, NoSolution
from .trajectory import plan_trapezoidal, plan_quintic, Trajectory
from .interpolator import Interpolator

__all__ = [
    "fk",
    "ik",
    "NoSolution",
    "plan_trapezoidal",
    "plan_quintic",
    "Trajectory",
    "Interpolator",
]
