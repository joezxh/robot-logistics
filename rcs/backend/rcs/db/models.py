"""SQLAlchemy ORM models for RCS Backend persistence.

Covers the data the backend owns: device registry/state, orders + their DAG
tasks, and topology (shell + grid). Used only when ``storage == "postgres"``
(or ``sqlite`` in async mode); an in-memory fallback keeps the app runnable
without a database.
"""
from __future__ import annotations
import datetime as dt
import uuid

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _uuid() -> str:
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    morphology: Mapped[str] = mapped_column(String(32), nullable=False)
    robot_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    num_joints: Mapped[int] = mapped_column(Integer, default=0)
    control_hz: Mapped[int] = mapped_column(Integer, default=0)
    mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    active_command_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    base_pose_in_world: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    scenario_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    deadline: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["OrderTask"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"), index=True
    )
    ref: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")


class OrderTask(Base):
    __tablename__ = "order_tasks"
    __table_args__ = (UniqueConstraint("order_id", "node_id", name="uq_order_task"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"), index=True
    )
    node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    slo_class: Mapped[str] = mapped_column(String(32), nullable=False)
    depends_on: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)

    order: Mapped["Order"] = relationship(back_populates="tasks")


class TopologyShell(Base):
    __tablename__ = "topology_shell"

    site_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    width_m: Mapped[float] = mapped_column(Float, default=0.0)
    depth_m: Mapped[float] = mapped_column(Float, default=0.0)
    height_m: Mapped[float] = mapped_column(Float, default=0.0)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TopologyGrid(Base):
    __tablename__ = "topology_grid"
    __table_args__ = (UniqueConstraint("site_id", "zone_id", name="uq_zone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(
        ForeignKey("topology_shell.site_id", ondelete="CASCADE"), index=True
    )
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False)
    zone_type: Mapped[int] = mapped_column(Integer, default=0)
    center_m: Mapped[list] = mapped_column(JSON, default=list)
    size_m: Mapped[list] = mapped_column(JSON, default=list)
    rotation_deg: Mapped[float] = mapped_column(Float, default=0.0)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
