-- RCS Backend — migration 007: create UnifiedMap + MapDynamicState, then
--                   one-time data migration merging the legacy
--                   TopologyShell + SiteMap tables into robot_unified_maps.
--
-- Background
-- ----------
-- The unified-map-model plan collapses the previously separate
-- `robot_topology_shell` (FloorShell geometry) and `robot_site_maps`
-- (node/edge navigation graph) into a single `robot_unified_maps` table, plus a
-- new dynamic layer `robot_map_dynamic_state`.
--
-- Legacy key convention (see migrations 005/006 and
-- `rcs.models.site_map_templates`):
--   * A warehouse template uses the SAME deterministic key `tpl-<key>` for
--     BOTH `robot_topology_shell.site_id` AND `robot_site_maps.map_id`.
--   * A live site uses an independent `site_id` (shell) and `map_id` (site map).
--
-- This migration:
--   Part A — CREATE the two new tables (idempotent, `IF NOT EXISTS`).
--   Part B — DATA MIGRATION: when `robot_unified_maps` is empty, build rows by
--            merging the legacy tables (idempotent, guarded with `WHERE NOT
--            EXISTS`). A pragmatic merge key is used (see comment in Part B).
--   Part C — DROP legacy tables. DEFERRED — kept commented out at the end of
--            this file. Tasks 3-7 still reference the old tables/ORM models, so
--            the actual DROP must wait until Task 7. See the OPTIONAL block.
--
-- NOTE: all JSON columns use `json` (NOT `jsonb`) to match the ORM in
-- `rcs.db.unified_map` (`sqlalchemy.JSON`), so `create_all` (dev/test) and this
-- migration stay in sync.
--
-- Safe to re-run: every statement is guarded with IF NOT EXISTS / IF EXISTS.
--
-- Apply with:
--   psql "$DATABASE_URL" -f migrations/007_unified_map.sql

-- ===========================================================================
-- Part A — CREATE the two new tables
-- ===========================================================================

CREATE TABLE IF NOT EXISTS robot_unified_maps (
    map_id          VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    name_en         VARCHAR(128),
    is_template     BOOLEAN DEFAULT FALSE,
    kind            VARCHAR(32),
    current_version INTEGER DEFAULT 1,
    bounds_json     JSON,
    geometry_json   JSON,
    topology_json   JSON,
    semantic_json   JSON,
    dynamic_json    JSON,
    data            JSON,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_map_dynamic_state (
    id          SERIAL PRIMARY KEY,
    map_id      VARCHAR(64) REFERENCES robot_unified_maps (map_id) ON DELETE CASCADE,
    element_id  VARCHAR(128),
    state       VARCHAR(64),
    payload     JSON,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT uq_map_dynamic_element UNIQUE (map_id, element_id)
);

-- Indexes mirror what SQLAlchemy generates for mapped_column(index=True).
CREATE INDEX IF NOT EXISTS ix_robot_map_dynamic_state_map_id
    ON robot_map_dynamic_state (map_id);
CREATE INDEX IF NOT EXISTS ix_robot_map_dynamic_state_element_id
    ON robot_map_dynamic_state (element_id);

-- ===========================================================================
-- Part B — DATA MIGRATION (ONE-TIME, IDEMPOTENT)
-- ===========================================================================
--
-- Merge key logic
-- ---------------
-- The unified map is keyed by `map_id`. We derive it from the navigation graph
-- side (`robot_site_maps.map_id`), because that is the primary "map" identity
-- used by the rest of the app. For each `robot_site_maps` row we pull geometry
-- (bounds / geometry / semantic) from the matching `robot_topology_shell` row
-- where `robot_topology_shell.site_id = robot_site_maps.map_id`. Templates use
-- the shared `tpl-<key>` key, so this join naturally pairs a template's shell
-- and site map; live sites pair their independent site_id/map_id when they
-- happen to share keys (otherwise geometry simply comes back NULL via LEFT
-- JOIN + COALESCE).
--
-- `is_template` is carried over from the site map row, and `kind` is set to
-- 'warehouse' when `is_template` is true, otherwise 'site'.
--
-- `topology_json` is built from the site map's `nodes_json`/`edges_json` graph;
-- `bounds_json`/`geometry_json`/`semantic_json` are pulled from the shell's
-- `data` JSON (COALESCE'd to '{}' so missing geometry never fails the insert).
-- `data` carries the raw shell `data` for non-lossy-ness.
--
-- The whole block is wrapped in `WHERE NOT EXISTS (SELECT 1 FROM
-- robot_unified_maps)` so re-running the migration never duplicates rows.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM robot_unified_maps) THEN
        INSERT INTO robot_unified_maps (
            map_id, name, name_en, is_template, kind,
            current_version, bounds_json, geometry_json,
            topology_json, semantic_json, dynamic_json, data,
            created_at, updated_at
        )
        SELECT
            sm.map_id,
            COALESCE(sm.name, sm.map_id)                          AS name,
            NULL                                                  AS name_en,
            COALESCE(sm.is_template, FALSE)                       AS is_template,
            CASE WHEN COALESCE(sm.is_template, FALSE) THEN 'warehouse'
                 ELSE 'site' END                                  AS kind,
            COALESCE(sm.current_version, 1)                       AS current_version,
            COALESCE(s.data->'bounds',  '{}'::json)               AS bounds_json,
            COALESCE(s.data,            '{}'::json)               AS geometry_json,
            json_build_object(
                'nodes', COALESCE(sm.nodes_json, '[]'::json),
                'edges', COALESCE(sm.edges_json, '[]'::json)
            )                                                     AS topology_json,
            COALESCE(s.data->'semantic', '{}'::json)              AS semantic_json,
            '{}'::json                                            AS dynamic_json,
            COALESCE(s.data,            '{}'::json)               AS data,
            COALESCE(sm.created_at, now())                        AS created_at,
            COALESCE(sm.updated_at, now())                        AS updated_at
        FROM robot_site_maps sm
        LEFT JOIN robot_topology_shell s
            ON s.site_id = sm.map_id;
    END IF;
END $$;

-- OPTIONAL: run only after Tasks 3-7 are complete and old ORM models removed.
-- These legacy tables are still referenced by the ORM/models during the
-- multi-task transition, so the DROP is intentionally NOT auto-applied above.
-- Uncomment and run by hand once nothing references them anymore:
--
-- DROP TABLE IF EXISTS robot_map_dynamic_state;
-- DROP TABLE IF EXISTS robot_topology_grid;
-- DROP TABLE IF EXISTS robot_site_map_versions;
-- DROP TABLE IF EXISTS robot_site_maps;
-- DROP TABLE IF EXISTS robot_topology_shell;
