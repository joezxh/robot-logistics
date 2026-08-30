"""Order persistence on the unified PostgreSQL backend (SQLAlchemy async)."""
from __future__ import annotations
import datetime as dt
import time
import uuid
from typing import Optional

from sqlalchemy import select, update as sa_update
from sqlalchemy.orm import selectinload

from rcs.db import models, session as db_session


class OrderRepository:
    # ---- create ----
    async def create(
        self,
        scenario_id: Optional[str],
        priority: int,
        deadline: Optional[float],
        items: list[dict],
        tasks: list[dict],
    ) -> dict:
        order_id = f"ORD-{uuid.uuid4().hex[:8]}"
        now = time.time()
        async for s in db_session.session():
            order = models.Order(
                order_id=order_id,
                scenario_id=scenario_id,
                priority=priority,
                deadline=deadline,
                status="queued",
                created_at=dt.datetime.fromtimestamp(now, dt.timezone.utc),
            )
            s.add(order)
            for it in items:
                s.add(models.OrderItem(order_id=order_id, ref=it["ref"], quantity=it["quantity"]))
            for t in tasks:
                s.add(models.OrderTask(
                    order_id=order_id,
                    node_id=t["node_id"],
                    task_type=t["task_type"],
                    slo_class=t["slo_class"],
                    depends_on=t.get("depends_on", []),
                    status="pending",
                ))
            await s.commit()
        return await self.get(order_id) or {
            "order_id": order_id, "scenario_id": scenario_id, "priority": priority,
            "deadline": deadline, "status": "queued", "created_at": now,
            "items": items, "tasks": tasks,
        }

    # ---- read ----
    async def get(self, order_id: str) -> Optional[dict]:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        async for s in db_session.session():
            stmt = (
                select(models.Order)
                .where(models.Order.order_id == order_id)
                .options(
                    selectinload(models.Order.items),
                    selectinload(models.Order.tasks),
                )
            )
            order = (await s.execute(stmt)).scalar_one_or_none()
            if order is None:
                return None
            items = [{"ref": i.ref, "quantity": i.quantity} for i in order.items]
            tasks = [
                {
                    "node_id": t.node_id,
                    "task_type": t.task_type,
                    "slo_class": t.slo_class,
                    "depends_on": t.depends_on or [],
                    "status": t.status,
                }
                for t in order.tasks
            ]
            return {
                "order_id": order.order_id,
                "scenario_id": order.scenario_id,
                "priority": order.priority,
                "deadline": order.deadline,
                "status": order.status,
                "created_at": order.created_at.timestamp(),
                "items": items,
                "tasks": tasks,
            }
        return None

    # ---- lifecycle / status machine ----
    async def list_orders(self, status: Optional[str] = None) -> list[dict]:
        async for s in db_session.session():
            stmt = select(models.Order).order_by(models.Order.created_at.desc())
            if status:
                stmt = stmt.where(models.Order.status == status)
            rows = (await s.execute(stmt)).scalars().all()
            out: list[dict] = []
            for order in rows:
                d = await self.get(order.order_id)
                if d is not None:
                    out.append(d)
            return out
        return []

    async def advance_status(self, order_id: str, status: str) -> bool:
        async for s in db_session.session():
            o = await s.get(models.Order, order_id)
            if o is None:
                return False
            o.status = status
            await s.commit()
            return True
        return False

    async def set_task_status(self, order_id: str, node_id: str, status: str) -> bool:
        async for s in db_session.session():
            stmt = (sa_update(models.OrderTask)
                    .where(models.OrderTask.order_id == order_id,
                           models.OrderTask.node_id == node_id)
                    .values(status=status))
            res = await s.execute(stmt)
            await s.commit()
            return res.rowcount > 0
        return False


repo = OrderRepository()