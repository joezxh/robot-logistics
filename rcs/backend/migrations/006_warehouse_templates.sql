-- RCS Backend — warehouse templates span all three topology tables.
--
-- A warehouse template is not just a navigation graph. To render on the 2D/3D
-- map and to be instantiable as a working site, it needs:
--
--   robot_site_maps      → navigation graph   (is_template added in 005)
--   robot_topology_shell → FloorShell geometry: bounds / walls / zones /
--                          facilities / docks / corridors / markings / floors
--   robot_topology_grid  → per-zone placement metadata
--
-- This migration adds the `is_template` flag to the two topology tables so a
-- template can live in the same tables as a real site while staying filterable.
-- Templates use a deterministic key of `tpl-<template_key>` for BOTH
-- `robot_topology_shell.site_id` and `robot_site_maps.map_id`, which makes
-- `seed_templates()` idempotent.
--
-- Safe to re-run: every statement is guarded with IF NOT EXISTS.
--
-- Apply with:
--   psql "$DATABASE_URL" -f migrations/006_warehouse_templates.sql

-- 1. FloorShell geometry (rendered by the 2D/3D map view).
ALTER TABLE robot_topology_shell
    ADD COLUMN IF NOT EXISTS is_template BOOLEAN NOT NULL DEFAULT FALSE;

-- Name matches what SQLAlchemy generates for `mapped_column(..., index=True)`.
CREATE INDEX IF NOT EXISTS ix_robot_topology_shell_is_template
    ON robot_topology_shell (is_template);

-- 2. Per-zone grid placement metadata.
ALTER TABLE robot_topology_grid
    ADD COLUMN IF NOT EXISTS is_template BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS ix_robot_topology_grid_is_template
    ON robot_topology_grid (is_template);
