-- RCS Backend — system-administration schema (v3)
-- Apply with:  psql "$DATABASE_URL" -f migrations/003_sys_admin.sql
--
-- The eight sys_* tables are provisioned by rcs/docs/sys.sql. This migration
-- only adds the columns/indexes the console needs on top of that dump, and is
-- safe to re-run (every statement is guarded with IF NOT EXISTS).
--
-- PRIVILEGES
-- ----------
-- If sys.sql was applied as `postgres` but the app connects as `rcs`, the
-- application role has no rights on these tables and seeding fails with
-- "permission denied for table sys_menu". Run once as the owning role:
--
--   GRANT USAGE ON SCHEMA public TO rcs;
--   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rcs;
--   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rcs;
--   ALTER DEFAULT PRIVILEGES IN SCHEMA public
--       GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rcs;
--   ALTER DEFAULT PRIVILEGES IN SCHEMA public
--       GRANT USAGE, SELECT ON SEQUENCES TO rcs;

-- ---------------------------------------------------------------------------
-- sys_menu: per-locale titles
-- ---------------------------------------------------------------------------
-- Shape: {"zh-CN": "设备管理", "zh-TW": "設備管理", "en-US": "Devices", "ja-JP": "デバイス管理"}
-- `name` remains the fallback rendered when a locale key is absent.
ALTER TABLE sys_menu ADD COLUMN IF NOT EXISTS i18n JSONB;

COMMENT ON COLUMN sys_menu.i18n IS '菜单多语言标题：{locale: title}，缺失时回退到 name';

-- Ensure the permission column is indexed — it is the natural key used by the
-- seeder and by every permission lookup.
CREATE INDEX IF NOT EXISTS idx_menu_permission ON sys_menu (permission) WHERE is_deleted = false;

-- ---------------------------------------------------------------------------
-- sys_audit_log: keep the username column searchable
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_audit_username ON sys_audit_log (username);

-- ---------------------------------------------------------------------------
-- sys_dictionary / sys_dictionary_item: soft-delete aware indexes
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dict_item_dict_active
    ON sys_dictionary_item (dict_code, is_active) WHERE is_deleted = false;
