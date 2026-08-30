"""Site TCP pose registry (placeholder).

Real site profiles are resolved by :func:`robot_contracts.get_site_profile`. This
submodule keeps the legacy ``from robot_contracts.site_tcp import ...`` import path
working until the site manager is fully wired in.
"""
from __future__ import annotations

from robot_contracts import Pose, get_site_profile

__all__ = ["get_site_tcp", "Pose", "get_site_profile"]


def get_site_tcp(site_id: str) -> Pose:
    """Return the TCP pose (in the robot base frame) for ``site_id``."""
    return get_site_profile(site_id).tcp_pose_in_base
