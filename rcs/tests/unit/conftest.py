"""Compatibility shim: add ``task_type`` / ``parameters`` to Command until Task 5 lands.

Task 3 and Task 4 tests instantiate ``Command`` with ``task_type`` and ``parameters``
keyword arguments. Those fields are scheduled to be added to ``Command`` by Task 5
(MQTT adapters). To keep Batch A tests runnable in isolation we patch ``Command``
at import time to accept the extra fields and store them as instance attributes.
"""
from __future__ import annotations

from rcs.rcs.state.command import Command

if "task_type" not in Command.__dataclass_fields__:
    _orig_init = Command.__init__

    def _patched_init(self, *args, **kwargs):  # type: ignore[no-redef]
        task_type = kwargs.pop("task_type", None)
        parameters = kwargs.pop("parameters", None)
        _orig_init(self, *args, **kwargs)
        self.task_type = task_type
        self.parameters = parameters

    Command.__init__ = _patched_init  # type: ignore[assignment]
