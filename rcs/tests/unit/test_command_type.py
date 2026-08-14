"""Test CommandType enum alignment with shared/contracts/command.schema.json."""
from __future__ import annotations

from rcs.rcs.state.command import CommandType
import json
from pathlib import Path


def test_execute_task_in_enum():
    assert hasattr(CommandType, "EXECUTE_TASK")
    assert CommandType.EXECUTE_TASK.value == "execute_task"


def test_enum_matches_contract_schema():
    schema_path = Path(__file__).resolve().parents[3] / "shared" / "contracts" / "command.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_types = set(schema["properties"]["type"]["enum"])
    enum_types = {ct.value for ct in CommandType}
    assert schema_types == enum_types, (
        f"Mismatch: schema has {schema_types - enum_types}, enum has {enum_types - schema_types}"
    )
