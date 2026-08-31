"""Unified Map Model ORM.

Adds :class:`UnifiedMap` (the single unified map table that converges the old
site-map / topology-shell / warehouse-map concepts) and :class:`MapDynamicState`
(the dynamic per-element state layer). The legacy ``TopologyShell`` /
``TopologyGrid`` / ``SiteMap`` / ``SiteMapVersion`` ORM classes have been removed;
their data now lives inside ``UnifiedMap`` (``geometry_json`` + ``topology_json``)
plus ``MapDynamicState``.

JSON columns use ``JSON`` (not ``JSONB``) to match the existing models in
``rcs.db.models`` and keep asyncpg compatibility.
"""
from __future__ import annotations
import datetime as dt

from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rcs.db.models import Base, _now


class UnifiedMap(Base):
    """The single unified map table.

    Converges geometry / topology / semantic / dynamic layers that were
    previously spread across ``robot_topology_shell`` + ``robot_site_maps``.
    """

    __tablename__ = "robot_unified_maps"

    map_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    bounds_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    geometry_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    topology_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    semantic_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dynamic_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    # ``dynamic_states`` is the one-to-many toward our own child table
    # (robot_map_dynamic_state), which is fully defined in this module.
    dynamic_states: Mapped[list["MapDynamicState"]] = relationship(
        back_populates="map", cascade="all, delete-orphan",
        passive_deletes=True, lazy="raise",
    )

    # NOTE: the one-to-many relationships toward ``TopologyGrid`` (grids) and
    # ``SiteMapVersion`` (versions) are intentionally NOT declared here yet.
    # Those child tables are still parented to their original tables
    # (robot_topology_shell / robot_site_maps) and have no foreign key to
    # robot_unified_maps, so declaring the relationships now would make SQLAlchemy
    # fail mapper initialization ("no foreign keys linking these tables"). Task 3
    # re-parents those child tables to UnifiedMap and adds the relationships then.


class MapDynamicState(Base):
    """Dynamic layer state for a map element (occupied / free / blocked / ...)."""

    __tablename__ = "robot_map_dynamic_state"
    __table_args__ = (
        UniqueConstraint("map_id", "element_id", name="uq_map_dynamic_element"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    map_id: Mapped[str] = mapped_column(
        ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"), index=True
    )
    element_id: Mapped[str] = mapped_column(String(128), index=True)
    state: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    map: Mapped["UnifiedMap"] = relationship(back_populates="dynamic_states")


__all__ = ["UnifiedMap", "MapDynamicState"]
