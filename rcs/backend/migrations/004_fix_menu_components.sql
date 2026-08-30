-- RCS Backend — fix sys_menu rows whose component/path were erroneously inserted
-- (e.g. pointing at the old `views/Admin*.vue` locations before the console
-- view tree was reorganised under views/control and views/topology).
--
-- Safe to re-run: every statement is a no-op when the row already holds the
-- correct value (the WHERE clause compares against the intended target).
--
-- Apply with:
--   psql "$DATABASE_URL" -f migrations/004_fix_menu_components.sql

-- ---------------------------------------------------------------------------
-- 1. Correct the `component` path for every relocated view.
--    Keyed by `permission` (the natural key used by the seeder and lookups).
-- ---------------------------------------------------------------------------
UPDATE sys_menu
SET component = 'views/control/AdminDevicesView.vue'
WHERE permission = 'sys:device:list'
  AND component IS DISTINCT FROM 'views/control/AdminDevicesView.vue';

UPDATE sys_menu
SET component = 'views/control/ControlView.vue'
WHERE permission = 'sys:device:control'
  AND component IS DISTINCT FROM 'views/control/ControlView.vue';

UPDATE sys_menu
SET component = 'views/topology/AdminMapsView.vue'
WHERE permission = 'sys:map:list'
  AND component IS DISTINCT FROM 'views/topology/AdminMapsView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminOrdersView.vue'
WHERE permission = 'sys:order:list'
  AND component IS DISTINCT FROM 'views/control/AdminOrdersView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminSchedulerView.vue'
WHERE permission = 'sys:scheduler:list'
  AND component IS DISTINCT FROM 'views/control/AdminSchedulerView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminLogsView.vue'
WHERE permission = 'sys:log:list'
  AND component IS DISTINCT FROM 'views/control/AdminLogsView.vue';

UPDATE sys_menu
SET component = 'views/topology/SiteMapView.vue'
WHERE permission = 'twin:sitemap:view'
  AND component IS DISTINCT FROM 'views/topology/SiteMapView.vue';

UPDATE sys_menu
SET component = 'views/topology/WarehouseView.vue'
WHERE permission = 'twin:warehouse:view'
  AND component IS DISTINCT FROM 'views/topology/WarehouseView.vue';

-- ---------------------------------------------------------------------------
-- 2. Guard: any *other* stale rows still referencing the old flat `views/`
--    location for one of the relocated files get remapped too. This catches
--    erroneously inserted duplicates that share the old path.
-- ---------------------------------------------------------------------------
UPDATE sys_menu
SET component = 'views/control/AdminDevicesView.vue'
WHERE component = 'views/AdminDevicesView.vue';

UPDATE sys_menu
SET component = 'views/control/ControlView.vue'
WHERE component = 'views/ControlView.vue';

UPDATE sys_menu
SET component = 'views/topology/AdminMapsView.vue'
WHERE component = 'views/AdminMapsView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminOrdersView.vue'
WHERE component = 'views/AdminOrdersView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminSchedulerView.vue'
WHERE component = 'views/AdminSchedulerView.vue';

UPDATE sys_menu
SET component = 'views/control/AdminLogsView.vue'
WHERE component = 'views/AdminLogsView.vue';

UPDATE sys_menu
SET component = 'views/topology/SiteMapView.vue'
WHERE component = 'views/SiteMapView.vue';

UPDATE sys_menu
SET component = 'views/topology/WarehouseView.vue'
WHERE component = 'views/WarehouseView.vue';
