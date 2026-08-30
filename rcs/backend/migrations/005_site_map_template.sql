-- RCS Backend — distinguish reusable warehouse templates from live site maps.
--
-- `robot_site_maps` had no way to tell a live, editable map apart from a
-- pre-built warehouse-type template. This adds a non-null `is_template` flag
-- (default FALSE) plus a supporting index so that:
--
--   * live map listings can exclude templates cheaply (no JSON inspection)
--   * the template seeder can be re-run idempotently, refreshing template
--     contents instead of inserting duplicates
--
-- Templates are seeded with deterministic, human-readable `map_id` values
-- (see `rcs.models.site_map_templates`), which is why the flag alone is enough
-- to key them — no extra `template_key` column is required.
--
-- Safe to re-run: both statements are guarded with IF NOT EXISTS.
--
-- Apply with:
--   psql "$DATABASE_URL" -f migrations/005_site_map_template.sql

ALTER TABLE robot_site_maps
    ADD COLUMN IF NOT EXISTS is_template BOOLEAN NOT NULL DEFAULT FALSE;

-- Name matches what SQLAlchemy generates for `mapped_column(..., index=True)`
-- so `create_all` (dev/test) and this migration stay in sync.
CREATE INDEX IF NOT EXISTS ix_robot_site_maps_is_template
    ON robot_site_maps (is_template);
