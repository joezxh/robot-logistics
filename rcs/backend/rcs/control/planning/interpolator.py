"""Step-through interpolator for a Trajectory."""
from __future__ import annotations
from .trajectory import Trajectory


class Interpolator:
    def __init__(self, traj: Trajectory, step_s: float = 0.001) -> None:
        self._traj = traj
        self._step_s = step_s
        self._elapsed_s = 0.0
        self._done = False

    @property
    def done(self) -> bool:
        return self._done

    @property
    def elapsed_s(self) -> float:
        return self._elapsed_s

    def next(self) -> list[float]:
        sample = self._traj.sample(self._elapsed_s)
        self._elapsed_s += self._step_s
        if self._elapsed_s >= self._traj.duration_s:
            self._done = True
        return sample
