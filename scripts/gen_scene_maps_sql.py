"""Emit 13 scene-map-template INSERT rows into 001_init.sql.

Reads ``docs/superpowers/specs/scene-map-templates.json`` (``wt_floor_shell``
schema) and appends an idempotent seed section to
``rcs/backend/migrations/001_init.sql``.

Canonical map_ids match ``control_unified_maps.SCENARIO_IDS`` (Python seeder)
so the SQL and Python sources coexist without overwriting each other. Each
scenario's first variant becomes the canonical row; further variants get a
``-<n>`` suffix and are SQL-only presets.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "superpowers" / "specs" / "scene-map-templates.json"
SQL_PATH = ROOT / "rcs" / "backend" / "migrations" / "001_init.sql"
SECTION_MARK = "-- 8. Scene-map scenario templates"

# Canonical map_id per scenario (mirrors control_unified_maps.SCENARIO_IDS).
CANONICAL = {
    "ecommerce": "tpl-ecommerce",
    "rail_unload": "tpl-train_unload",
    "manufacturing": "tpl-manufacturing",
    "port": "tpl-port",
    "cold_chain": "tpl-scn-cold_chain",
    "reverse_logistics": "tpl-scn-reverse_logistics",
    "multi_floor": "tpl-multi_floor",
}


def sql_escape(text: str) -> str:
    """Escape a Python string for a single-quoted PostgreSQL literal."""
    return text.replace("\\", "\\\\").replace("'", "''")


def json_literal(obj) -> str:
    """Render a python object as a ``::json`` SQL literal."""
    raw = json.dumps(obj, ensure_ascii=False)
    return "'" + sql_escape(raw) + "'::json"


def derive_map_ids(templates: list[dict]) -> list[tuple[str, dict]]:
    """Return ordered list of (map_id, template) with canonical primary ids."""
    seen: dict[str, int] = {}
    out: list[tuple[str, dict]] = []
    for t in templates:
        s = t["meta"]["scenario"]
        if s not in seen:
            seen[s] = 0
            map_id = CANONICAL[s]
        else:
            seen[s] += 1
            map_id = f"{CANONICAL[s]}-{seen[s]}"
        out.append((map_id, t))
    return out


def build_semantic(t: dict) -> dict:
    meta = t["meta"]
    sem = {
        "scenario": meta["scenario"],
        "variant": meta["variant"],
        "reference": meta.get("reference", ""),
    }
    if meta["scenario"] == "rail_unload":
        sem["flow"] = ["rail_track", "train_car", "platform", "truck"]
    return sem


def build_bounds(t: dict) -> dict:
    b = dict(t.get("bounds", {}))
    out = {"w": b.get("w"), "d": b.get("d")}
    if "h" in b:
        out["h"] = b["h"]
    return out


def build_rows(templates: list[dict]) -> str:
    parts: list[str] = []
    for map_id, t in derive_map_ids(templates):
        meta = t["meta"]
        name = meta["name"]
        name_en = meta["name_en"]
        geo = {k: v for k, v in t.items() if k != "meta"}
        bounds = build_bounds(t)
        sem = build_semantic(t)
        vals = (
            f"    ('{sql_escape(map_id)}',"
            f" '{sql_escape(name)}',"
            f" '{sql_escape(name_en)}',"
            f" TRUE,"
            f" 'scenario',"
            f" 1,"
            f" {json_literal(bounds)},"
            f" {json_literal(geo)},"
            f" '{{}}'::json,"
            f" {json_literal(sem)},"
            f" '{{}}'::json,"
            f" '{{}}'::json)"
        )
        parts.append(vals)
    return ",\n".join(parts)


def build_section(templates: list[dict]) -> str:
    rows = build_rows(templates)
    return (
        f"\n\n{SECTION_MARK}\n"
        "-- 13 init scene-map templates (7 canonical primary rows match Python\n"
        "-- SCENARIO_IDS; 6 secondary variants are SQL-only presets). Idempotent.\n"
        "INSERT INTO robot_unified_maps (\n"
        "    map_id, name, name_en, is_template, kind, current_version,\n"
        "    bounds_json, geometry_json, topology_json, semantic_json,\n"
        "    dynamic_json, data\n"
        ")\n"
        "VALUES\n"
        f"{rows}\n"
        "ON CONFLICT (map_id) DO UPDATE SET\n"
        "    name = EXCLUDED.name,\n"
        "    name_en = EXCLUDED.name_en,\n"
        "    is_template = EXCLUDED.is_template,\n"
        "    kind = EXCLUDED.kind,\n"
        "    current_version = EXCLUDED.current_version,\n"
        "    bounds_json = EXCLUDED.bounds_json,\n"
        "    geometry_json = EXCLUDED.geometry_json,\n"
        "    topology_json = EXCLUDED.topology_json,\n"
        "    semantic_json = EXCLUDED.semantic_json,\n"
        "    dynamic_json = EXCLUDED.dynamic_json,\n"
        "    data = EXCLUDED.data;\n"
    )


def main() -> None:
    templates = json.loads(JSON_PATH.read_text(encoding="utf-8"))["templates"]
    section = build_section(templates)
    sql = SQL_PATH.read_text(encoding="utf-8")
    if SECTION_MARK in sql:
        # Replace existing section for idempotent re-runs.
        sql = re.sub(re.escape(SECTION_MARK) + r".*?;\n", "", sql, flags=re.S)
        # Remove trailing blank lines introduced.
        sql = sql.rstrip() + "\n"
    sql = sql.rstrip() + section
    SQL_PATH.write_text(sql, encoding="utf-8")
    print(f"Wrote {len(templates)} scene-map rows into {SQL_PATH.name}")


if __name__ == "__main__":
    main()
