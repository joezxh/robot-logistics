-- ===========================================================================
-- RCS Backend — consolidated schema (single source of truth)
-- ===========================================================================
--
-- This file is the MERGE of migrations 001_init .. 007_unified_map. Every
-- intermediate step (table renames, column back-fills, one-off data copies,
-- legacy-table drops) has been folded into the FINAL table definitions so a
-- fresh database can be created with a single file.
--
-- Authority: rcs/db/models.py (+ rcs/db/unified_map.py, rcs/db/sys_models.py).
-- The result is identical to what `init_db()` produces via
-- `Base.metadata.create_all` — this file just makes the schema reviewable and
-- lets deployments that do NOT rely on create_all provision the DB directly.
--
-- How the 7 legacy migrations collapsed into this file:
--   001_init.sql        -> the six core tables (device / order / topology) below
--   002_rename_tables   -> NO-OP here: a fresh DB already uses the robot_ prefix
--   003_sys_admin       -> sys_menu.i18n folded into the sys_menu CREATE; the
--                          three indexes below are created directly
--   004_fix_menu_cmps   -> the relocated component paths are now part of the
--                          INSERT seed rows in the "Seed data" section, so the
--                          standalone UPDATEs are no longer needed
--   005_site_map_tpl    -> is_template flag is part of robot_unified_maps / the
--                          topology tables' final shape (no standalone ALTER)
--   006_warehouse_tpl   -> same as 005
--   007_unified_map     -> robot_unified_maps + robot_map_dynamic_state created
--                          directly; the legacy topology tables
--                          (robot_topology_shell / robot_topology_grid /
--                          robot_site_maps) are intentionally NOT created here —
--                          they were superseded by the unified-map model and the
--                          ORM no longer defines them. The data-migration block
--                          (copying from those legacy tables) is dropped because a
--                          fresh DB has nothing to copy from.
--
-- NOTE: rcs/db/models.py also defines robot_planning_profiles,
-- robot_scheduler_configs, robot_command_logs, robot_event_logs and the four
-- wms_* tables. They were never covered by any migration file and are generated
-- by create_all at runtime; they ARE included below so this init is a complete
-- schema. If you keep using create_all you can ignore them — they will simply
-- already exist.
--
-- Apply:  psql "$DATABASE_URL" -f migrations/001_init.sql
-- Or let the app auto-create tables on startup (init_db) when storage=postgres.
-- Every statement is idempotent (IF NOT EXISTS / guarded) so re-running is safe.
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- 1. Core domain — devices, orders, tasks
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS robot_devices (
    device_id           VARCHAR(64) PRIMARY KEY,
    morphology          VARCHAR(32)  NOT NULL,
    robot_type          VARCHAR(32),
    num_joints          INTEGER       NOT NULL DEFAULT 0,
    control_hz          INTEGER       NOT NULL DEFAULT 0,
    mode                VARCHAR(32),
    active_command_id   VARCHAR(64),
    last_error          TEXT,
    locked              BOOLEAN       NOT NULL DEFAULT FALSE,
    base_pose_in_world  JSONB,
    -- Persisted device spec / params (Phase B)
    spec_json           JSONB         DEFAULT '{}'::jsonb,
    limits_json         JSONB         DEFAULT '{}'::jsonb,
    home_joints_json    JSONB         DEFAULT '[]'::jsonb,
    status              VARCHAR(32)   DEFAULT 'registered',
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_orders (
    order_id            VARCHAR(64) PRIMARY KEY,
    scenario_id         VARCHAR(64),
    priority            INTEGER       NOT NULL DEFAULT 5,
    deadline            DOUBLE PRECISION,
    status              VARCHAR(32)   NOT NULL DEFAULT 'queued',
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_order_items (
    id                  BIGSERIAL PRIMARY KEY,
    order_id            VARCHAR(64)  NOT NULL REFERENCES robot_orders (order_id) ON DELETE CASCADE,
    ref                 VARCHAR(128) NOT NULL,
    quantity            INTEGER       NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS robot_order_tasks (
    id                  BIGSERIAL PRIMARY KEY,
    order_id            VARCHAR(64)  NOT NULL REFERENCES robot_orders (order_id) ON DELETE CASCADE,
    node_id             VARCHAR(64)  NOT NULL,
    task_type           VARCHAR(32)  NOT NULL,
    slo_class           VARCHAR(32)  NOT NULL,
    depends_on          JSONB         NOT NULL DEFAULT '[]'::jsonb,
    status              VARCHAR(32)   NOT NULL DEFAULT 'pending',
    CONSTRAINT uq_order_task UNIQUE (order_id, node_id)
);

-- ---------------------------------------------------------------------------
-- 2. Planning / scheduling / logs (defined in rcs/db/models.py)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS robot_planning_profiles (
    profile_id          VARCHAR(64) PRIMARY KEY,
    name                VARCHAR(128) NOT NULL,
    algo                VARCHAR(32)  NOT NULL,
    axes                INTEGER       NOT NULL DEFAULT 6,
    vel_max_json        JSONB         DEFAULT '[]'::jsonb,
    acc_max_json        JSONB         DEFAULT '[]'::jsonb,
    created_by          VARCHAR(64),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_scheduler_configs (
    config_id           VARCHAR(64) PRIMARY KEY,
    name                VARCHAR(128) NOT NULL,
    strategy            VARCHAR(32)   DEFAULT 'util-weighted',
    weights_json        JSONB         DEFAULT '{}'::jsonb,
    active              BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_command_logs (
    cmd_id              VARCHAR(64) PRIMARY KEY,
    device_id           VARCHAR(64),
    cmd_type            VARCHAR(32)  NOT NULL,
    payload_json        JSONB         DEFAULT '{}'::jsonb,
    issued_by           VARCHAR(64),
    result              VARCHAR(16)   DEFAULT 'ok',
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_event_logs (
    event_id            VARCHAR(64) PRIMARY KEY,
    level               VARCHAR(16)   DEFAULT 'info',
    source              VARCHAR(64),
    message             TEXT          NOT NULL,
    meta_json           JSONB         DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 3. Warehouse inventory domain (WMS)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS wms_slots (
    id                  BIGSERIAL PRIMARY KEY,
    site_id             VARCHAR(64)   DEFAULT 'warehouse-theatre-3d',
    group_id            VARCHAR(64),
    label               VARCHAR(64),
    row                 INTEGER       NOT NULL DEFAULT 0,
    col                 INTEGER       NOT NULL DEFAULT 0,
    row_gap             DOUBLE PRECISION DEFAULT 0.0,
    occ                 DOUBLE PRECISION DEFAULT 0.0,   -- 0..1 utilisation
    levels              JSONB         DEFAULT '[]'::jsonb,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wms_inventory_items (
    id                  BIGSERIAL PRIMARY KEY,
    site_id             VARCHAR(64)   DEFAULT 'warehouse-theatre-3d',
    slot_id             INTEGER       NOT NULL REFERENCES wms_slots (id) ON DELETE CASCADE,
    level_label         VARCHAR(64)   NOT NULL,
    item_code           VARCHAR(64)   NOT NULL,
    item_name           VARCHAR(128)  NOT NULL,
    uom                 VARCHAR(16)   DEFAULT 'EA',
    grp                 VARCHAR(64)   DEFAULT '',
    qty                 DOUBLE PRECISION DEFAULT 0.0,
    reserved            DOUBLE PRECISION DEFAULT 0.0,
    rate                DOUBLE PRECISION DEFAULT 0.0,  -- throughput / day
    stock_value         DOUBLE PRECISION DEFAULT 0.0,
    CONSTRAINT uq_wms_item_slot_level UNIQUE (slot_id, level_label, item_code)
);

CREATE TABLE IF NOT EXISTS wms_agvs (
    id                  BIGSERIAL PRIMARY KEY,
    site_id             VARCHAR(64)   DEFAULT 'warehouse-theatre-3d',
    ref                 VARCHAR(64),
    name                VARCHAR(128)  DEFAULT '',
    x                   DOUBLE PRECISION DEFAULT 0.0,
    z                   DOUBLE PRECISION DEFAULT 0.0,
    yaw                 DOUBLE PRECISION DEFAULT 0.0,
    battery             DOUBLE PRECISION DEFAULT 1.0,  -- 0..1
    status              VARCHAR(16)   DEFAULT 'idle',   -- idle|moving|charging|fault
    current_task        VARCHAR(64),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wms_logistics_tasks (
    id                  BIGSERIAL PRIMARY KEY,
    site_id             VARCHAR(64)   DEFAULT 'warehouse-theatre-3d',
    ref                 VARCHAR(64),
    type                VARCHAR(16)   NOT NULL,         -- inbound|outbound|transfer|replenishment
    status              VARCHAR(16)   DEFAULT 'pending',-- pending|in_progress|completed|cancelled
    priority            INTEGER       NOT NULL DEFAULT 5,
    source_dock         VARCHAR(64),
    target_dock         VARCHAR(64),
    items               JSONB         DEFAULT '[]'::jsonb,
    assigned_vehicle    VARCHAR(64),
    eta                 INTEGER,
    completed_at        INTEGER,
    created_at          INTEGER       NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- 4. Unified map model (was migration 007; supersedes the legacy
--    robot_topology_shell / robot_topology_grid / robot_site_maps tables)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS robot_unified_maps (
    map_id              VARCHAR(64) PRIMARY KEY,
    name                VARCHAR(128) NOT NULL,
    name_en             VARCHAR(128),
    is_template         BOOLEAN       DEFAULT FALSE,
    kind                VARCHAR(32),
    current_version     INTEGER       DEFAULT 1,
    bounds_json         JSON,
    geometry_json       JSON,
    topology_json       JSON,
    semantic_json       JSON,
    dynamic_json        JSON,
    data                JSON,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_map_dynamic_state (
    id                  SERIAL PRIMARY KEY,
    map_id              VARCHAR(64)  REFERENCES robot_unified_maps (map_id) ON DELETE CASCADE,
    element_id          VARCHAR(128),
    state               VARCHAR(64),
    payload             JSON,
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    CONSTRAINT uq_map_dynamic_element UNIQUE (map_id, element_id)
);

-- ---------------------------------------------------------------------------
-- 5. System-administration tables (rcs/db/sys_models.py)
--    Full DDL is owned by the sys seeder / create_all; the only extension that
--    lived in a migration is sys_menu.i18n (folded into the CREATE below).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sys_user (
    user_id             BIGSERIAL PRIMARY KEY,
    username            VARCHAR(50)  NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    real_name           VARCHAR(100) NOT NULL,
    phone               VARCHAR(20),
    email               VARCHAR(100),
    avatar_url          VARCHAR(500),
    status              VARCHAR(20)  NOT NULL DEFAULT 'active',
    is_admin            BOOLEAN      NOT NULL DEFAULT FALSE,
    last_login_at       TIMESTAMP,
    last_login_ip       VARCHAR(50),
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMP,
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_sys_user_username UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS sys_role (
    role_id             BIGSERIAL PRIMARY KEY,
    role_name           VARCHAR(100) NOT NULL,
    role_code           VARCHAR(50)  NOT NULL,
    region_code         VARCHAR(20),
    region_level        VARCHAR(20),
    description         TEXT,
    sort_order          INTEGER       NOT NULL DEFAULT 0,
    status              VARCHAR(20)  NOT NULL DEFAULT 'active',
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT now(),
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_sys_role_role_code UNIQUE (role_code)
);

CREATE TABLE IF NOT EXISTS sys_user_role (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT       NOT NULL REFERENCES sys_user (user_id),
    role_id             BIGINT       NOT NULL REFERENCES sys_role (role_id),
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    CONSTRAINT uk_sys_user_role UNIQUE (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS sys_menu (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    path                VARCHAR(255),
    parent_id           BIGINT       DEFAULT 0,
    sort                INTEGER       NOT NULL DEFAULT 0,
    status              INTEGER       NOT NULL DEFAULT 0,
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT now(),
    permission          VARCHAR(100),
    type                INTEGER       NOT NULL DEFAULT 2,   -- 1=dir 2=menu 3=btn
    icon                VARCHAR(100),
    component           VARCHAR(255),
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    component_name      VARCHAR(100),
    visible             INTEGER       NOT NULL DEFAULT 1,
    keep_alive          INTEGER       NOT NULL DEFAULT 0,
    always_show         INTEGER       NOT NULL DEFAULT 0,
    -- Extension formerly added by migration 003_sys_admin.sql
    i18n                JSONB
);

CREATE TABLE IF NOT EXISTS sys_role_menu (
    id                  BIGSERIAL PRIMARY KEY,
    role_id             BIGINT       NOT NULL REFERENCES sys_role (role_id),
    menu_id             BIGINT       NOT NULL REFERENCES sys_menu (id) ON DELETE CASCADE,
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    CONSTRAINT uk_sys_role_menu UNIQUE (role_id, menu_id)
);

CREATE TABLE IF NOT EXISTS sys_audit_log (
    log_id              BIGSERIAL PRIMARY KEY,
    user_id             BIGINT,
    username            VARCHAR(50),
    operation_type      VARCHAR(50)  NOT NULL,
    operation_module    VARCHAR(50),
    operation_desc      TEXT,
    request_method      VARCHAR(10),
    request_url         VARCHAR(500),
    request_params      JSONB,
    request_ip          VARCHAR(50),
    user_agent          VARCHAR(500),
    response_status     INTEGER,
    response_time_ms    INTEGER,
    old_data            JSONB,
    new_data            JSONB,
    created_at          TIMESTAMP    NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sys_dictionary (
    dict_id             BIGSERIAL PRIMARY KEY,
    dict_code           VARCHAR(50)  NOT NULL,
    dict_name           VARCHAR(100) NOT NULL,
    dict_type           VARCHAR(50)  NOT NULL,
    description         TEXT,
    sort_order          INTEGER       NOT NULL DEFAULT 0,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    extra_data          JSONB,
    created_by          BIGINT,
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT now(),
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_sys_dict_code UNIQUE (dict_code)
);

CREATE TABLE IF NOT EXISTS sys_dictionary_item (
    item_id             BIGSERIAL PRIMARY KEY,
    dict_code           VARCHAR(50)  NOT NULL,
    item_code           VARCHAR(50)  NOT NULL,
    item_name           VARCHAR(100) NOT NULL,
    item_value          VARCHAR(200),
    parent_code         VARCHAR(50),
    level               INTEGER       NOT NULL DEFAULT 1,
    color               VARCHAR(20),
    icon                VARCHAR(50),
    sort_order          INTEGER       NOT NULL DEFAULT 0,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    extra_data          JSONB,
    remark              TEXT,
    created_by          BIGINT,
    created_at          TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT now(),
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_sys_dict_item UNIQUE (dict_code, item_code)
);

-- ---------------------------------------------------------------------------
-- 6. Indexes (mirror what SQLAlchemy generates for mapped_column(index=True)
--    plus the soft-delete-aware indexes from migration 003_sys_admin.sql)
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS ix_robot_devices_status
    ON robot_devices (status);
CREATE INDEX IF NOT EXISTS ix_robot_orders_scenario_id
    ON robot_orders (scenario_id);
CREATE INDEX IF NOT EXISTS ix_robot_orders_status
    ON robot_orders (status);
CREATE INDEX IF NOT EXISTS ix_robot_order_items_order_id
    ON robot_order_items (order_id);
CREATE INDEX IF NOT EXISTS ix_robot_order_tasks_order_id
    ON robot_order_tasks (order_id);
CREATE INDEX IF NOT EXISTS ix_robot_order_tasks_status
    ON robot_order_tasks (status);
CREATE INDEX IF NOT EXISTS ix_robot_scheduler_configs_active
    ON robot_scheduler_configs (active);
CREATE INDEX IF NOT EXISTS ix_robot_command_logs_device_id
    ON robot_command_logs (device_id);
CREATE INDEX IF NOT EXISTS ix_robot_command_logs_created_at
    ON robot_command_logs (created_at);
CREATE INDEX IF NOT EXISTS ix_robot_event_logs_level
    ON robot_event_logs (level);
CREATE INDEX IF NOT EXISTS ix_robot_event_logs_source
    ON robot_event_logs (source);
CREATE INDEX IF NOT EXISTS ix_robot_event_logs_created_at
    ON robot_event_logs (created_at);
CREATE INDEX IF NOT EXISTS ix_wms_slots_site_id
    ON wms_slots (site_id);
CREATE INDEX IF NOT EXISTS ix_wms_slots_group_id
    ON wms_slots (group_id);
CREATE INDEX IF NOT EXISTS ix_wms_slots_label
    ON wms_slots (label);
CREATE INDEX IF NOT EXISTS ix_wms_inventory_items_slot_id
    ON wms_inventory_items (slot_id);
CREATE INDEX IF NOT EXISTS ix_wms_inventory_items_item_code
    ON wms_inventory_items (item_code);
CREATE INDEX IF NOT EXISTS ix_wms_agvs_site_id
    ON wms_agvs (site_id);
CREATE INDEX IF NOT EXISTS ix_wms_agvs_ref
    ON wms_agvs (ref);
CREATE INDEX IF NOT EXISTS ix_wms_logistics_tasks_site_id
    ON wms_logistics_tasks (site_id);
CREATE INDEX IF NOT EXISTS ix_wms_logistics_tasks_ref
    ON wms_logistics_tasks (ref);
CREATE INDEX IF NOT EXISTS ix_robot_map_dynamic_state_map_id
    ON robot_map_dynamic_state (map_id);
CREATE INDEX IF NOT EXISTS ix_robot_map_dynamic_state_element_id
    ON robot_map_dynamic_state (element_id);

CREATE INDEX IF NOT EXISTS idx_user_status        ON sys_user (status);
CREATE INDEX IF NOT EXISTS idx_role_code          ON sys_role (role_code);
CREATE INDEX IF NOT EXISTS idx_role_region         ON sys_role (region_code);
CREATE INDEX IF NOT EXISTS idx_user_role_role      ON sys_user_role (role_id);
CREATE INDEX IF NOT EXISTS idx_menu_parent_id      ON sys_menu (parent_id);
CREATE INDEX IF NOT EXISTS idx_menu_status         ON sys_menu (status);
CREATE INDEX IF NOT EXISTS idx_menu_type           ON sys_menu (type);
CREATE INDEX IF NOT EXISTS idx_audit_operation     ON sys_audit_log (operation_type, operation_module);
CREATE INDEX IF NOT EXISTS idx_audit_user          ON sys_audit_log (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_time          ON sys_audit_log (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_ip            ON sys_audit_log (request_ip);
CREATE INDEX IF NOT EXISTS idx_dict_type           ON sys_dictionary (dict_type);
CREATE INDEX IF NOT EXISTS idx_dict_active         ON sys_dictionary (is_active);
CREATE INDEX IF NOT EXISTS idx_item_dict_code      ON sys_dictionary_item (dict_code);
CREATE INDEX IF NOT EXISTS idx_item_code           ON sys_dictionary_item (item_code);
CREATE INDEX IF NOT EXISTS idx_item_parent         ON sys_dictionary_item (parent_code);
CREATE INDEX IF NOT EXISTS idx_item_active         ON sys_dictionary_item (is_active);

-- Soft-delete-aware / natural-key indexes formerly created by 003_sys_admin.sql
CREATE INDEX IF NOT EXISTS idx_menu_permission
    ON sys_menu (permission) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_audit_username
    ON sys_audit_log (username);
CREATE INDEX IF NOT EXISTS idx_dict_item_dict_active
    ON sys_dictionary_item (dict_code, is_active) WHERE is_deleted = false;

-- ---------------------------------------------------------------------------
-- 7. Seed data — initial menu / role / user catalogue
-- ---------------------------------------------------------------------------
-- This mirrors rcs/services/sys/sys_seed.py (the runtime seeder gated by
-- RCS_SYS_SEED_ON_STARTUP) so a database can be fully provisioned from this
-- single file without relying on create_all + the Python seeder.
--
-- All INSERTs are idempotent (ON CONFLICT DO NOTHING) so re-running the file is
-- safe. Menu / role / user ids are hard-coded to keep the parent links and the
-- sys_role_menu / sys_user_role grants consistent. The serial sequences are
-- advanced afterwards so the app can keep auto-issuing ids past the seed rows.
--
-- Default password for every seeded account is RCS_SYS_DEFAULT_PASSWORD
-- ("rcs@2026"); the bcrypt hash below was produced by the same algorithm the
-- app uses (rcs/services/sys/sys_security.get_password_hash). Change it after
-- first login.
-- ---------------------------------------------------------------------------

-- 7a. Menus (type: 1=目录 / 2=菜单 / 3=按钮)
INSERT INTO sys_menu (id, name, path, parent_id, sort, status, permission, type, icon, component, component_name, visible, keep_alive, always_show, i18n)
VALUES
  (1,  '控制台',     '/dashboard',   0,  1, 0, 'dashboard:view',      2, 'DashboardOutlined',    'views/DashboardView.vue',         'DashboardView',         1, 0, 0, '{"zh-CN":"控制台","zh-TW":"控制檯","en-US":"Dashboard","ja-JP":"ダッシュボード"}'::jsonb),
  (2,  '设备管理',   '/devices',     0, 10, 0, 'device:menu',         1, 'RobotOutlined',        NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"设备管理","zh-TW":"設備管理","en-US":"Devices","ja-JP":"デバイス管理"}'::jsonb),
  (3,  '设备列表',   '/devices',     2,  1, 0, 'sys:device:list',     2, 'UnorderedListOutlined','views/control/AdminDevicesView.vue','AdminDevicesView',    1, 0, 0, '{"zh-CN":"设备列表","zh-TW":"設備列表","en-US":"Device List","ja-JP":"デバイス一覧"}'::jsonb),
  (4,  '设备控制',   '/control',     2,  2, 0, 'sys:device:control',  2, 'ControlOutlined',      'views/control/ControlView.vue',   'ControlView',           1, 0, 0, '{"zh-CN":"设备控制","zh-TW":"設備控制","en-US":"Device Control","ja-JP":"デバイス制御"}'::jsonb),
  (5,  '仓储作业',   '/wms',         0, 20, 0, 'wms:menu',            1, 'AppstoreOutlined',     NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"仓储作业","zh-TW":"倉儲作業","en-US":"Warehouse Ops","ja-JP":"倉庫作業"}'::jsonb),
  (6,  '场景地图',   '/admin/maps',  5,  1, 0, 'sys:map:list',        2, 'EnvironmentOutlined',   'views/topology/AdminMapsView.vue','AdminMapsView',        1, 0, 0, '{"zh-CN":"场景地图","zh-TW":"場景地圖","en-US":"Site Maps","ja-JP":"サイトマップ"}'::jsonb),

  (7,  '订单管理',   '/admin/orders',5,  2, 0, 'sys:order:list',      2, 'ShoppingOutlined',     'views/control/AdminOrdersView.vue','AdminOrdersView',      1, 0, 0, '{"zh-CN":"订单管理","zh-TW":"訂單管理","en-US":"Orders","ja-JP":"オーダー管理"}'::jsonb),
  (8,  '调度策略',   '/admin/scheduler',5,3, 0, 'sys:scheduler:list',  2, 'DeploymentUnitOutlined','views/control/AdminSchedulerView.vue','AdminSchedulerView', 1, 0, 0, '{"zh-CN":"调度策略","zh-TW":"調度策略","en-US":"Scheduler","ja-JP":"スケジューラ"}'::jsonb),
  (9,  '系统日志',   '/admin/logs',  5,  4, 0, 'sys:log:list',        2, 'FileTextOutlined',     'views/control/AdminLogsView.vue','AdminLogsView',         1, 0, 0, '{"zh-CN":"系统日志","zh-TW":"系統日誌","en-US":"System Logs","ja-JP":"システムログ"}'::jsonb),



  (13, '系统管理',   '/system',      0, 90, 0, 'system:menu',         1, 'SettingOutlined',      NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"系统管理","zh-TW":"系統管理","en-US":"System","ja-JP":"システム管理"}'::jsonb),
  (14, '用户管理',   '/system/users',13, 1, 0, 'sys:user:list',       2, 'UserOutlined',         'views/system/UserManage.vue',    'UserManage',            1, 0, 0, '{"zh-CN":"用户管理","zh-TW":"用戶管理","en-US":"Users","ja-JP":"ユーザー管理"}'::jsonb),
  (15, '新增',       NULL,           14,80, 0, 'sys:user:create',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"新增","zh-TW":"新增","en-US":"Create","ja-JP":"作成"}'::jsonb),
  (16, '修改',       NULL,           14,81, 0, 'sys:user:update',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"修改","zh-TW":"修改","en-US":"Update","ja-JP":"更新"}'::jsonb),
  (17, '删除',       NULL,           14,82, 0, 'sys:user:delete',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"删除","zh-TW":"刪除","en-US":"Delete","ja-JP":"削除"}'::jsonb),
  (18, '角色管理',   '/system/roles',13, 2, 0, 'sys:role:list',       2, 'SafetyCertificateOutlined','views/system/RoleManage.vue', 'RoleManage',            1, 0, 0, '{"zh-CN":"角色管理","zh-TW":"角色管理","en-US":"Roles","ja-JP":"ロール管理"}'::jsonb),
  (19, '新增',       NULL,           18,80, 0, 'sys:role:create',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"新增","zh-TW":"新增","en-US":"Create","ja-JP":"作成"}'::jsonb),
  (20, '修改',       NULL,           18,81, 0, 'sys:role:update',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"修改","zh-TW":"修改","en-US":"Update","ja-JP":"更新"}'::jsonb),
  (21, '删除',       NULL,           18,82, 0, 'sys:role:delete',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"删除","zh-TW":"刪除","en-US":"Delete","ja-JP":"削除"}'::jsonb),
  (22, '菜单管理',   '/system/menus',13, 3, 0, 'sys:menu:list',       2, 'MenuOutlined',         'views/system/MenuManage.vue',    'MenuManage',            1, 0, 0, '{"zh-CN":"菜单管理","zh-TW":"選單管理","en-US":"Menus","ja-JP":"メニュー管理"}'::jsonb),
  (23, '新增',       NULL,           22,80, 0, 'sys:menu:create',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"新增","zh-TW":"新增","en-US":"Create","ja-JP":"作成"}'::jsonb),
  (24, '修改',       NULL,           22,81, 0, 'sys:menu:update',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"修改","zh-TW":"修改","en-US":"Update","ja-JP":"更新"}'::jsonb),
  (25, '删除',       NULL,           22,82, 0, 'sys:menu:delete',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"删除","zh-TW":"刪除","en-US":"Delete","ja-JP":"削除"}'::jsonb),
  (26, '字典管理',   '/system/dicts',13, 5, 0, 'sys:dict:list',       2, 'BookOutlined',         'views/system/DictManage.vue',    'DictManage',            1, 0, 0, '{"zh-CN":"字典管理","zh-TW":"字典管理","en-US":"Dictionaries","ja-JP":"辞書管理"}'::jsonb),
  (27, '新增',       NULL,           26,80, 0, 'sys:dict:create',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"新增","zh-TW":"新增","en-US":"Create","ja-JP":"作成"}'::jsonb),
  (28, '修改',       NULL,           26,81, 0, 'sys:dict:update',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"修改","zh-TW":"修改","en-US":"Update","ja-JP":"更新"}'::jsonb),
  (29, '删除',       NULL,           26,82, 0, 'sys:dict:delete',     3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"删除","zh-TW":"刪除","en-US":"Delete","ja-JP":"削除"}'::jsonb),
  (30, '重置密码',   NULL,           14,95, 0, 'sys:user:reset-password',3,NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"重置密码","zh-TW":"重設密碼","en-US":"Reset Password","ja-JP":"パスワードリセット"}'::jsonb),
  (31, '分配角色',   NULL,           14,96, 0, 'sys:user:assign-role', 3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"分配角色","zh-TW":"分配角色","en-US":"Assign Roles","ja-JP":"ロール割当"}'::jsonb),
  (32, '分配菜单',   NULL,           18,97, 0, 'sys:role:assign-menu', 3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"分配菜单","zh-TW":"分配選單","en-US":"Assign Menus","ja-JP":"メニュー割当"}'::jsonb),
  (33, '审计日志',   '/system/audit',13, 4, 0, 'sys:audit:list',      2, 'HistoryOutlined',      'views/system/AuditLog.vue',      'AuditLog',              1, 0, 0, '{"zh-CN":"审计日志","zh-TW":"稽核日誌","en-US":"Audit Logs","ja-JP":"監査ログ"}'::jsonb),
  (34, '清理日志',   NULL,           33,98, 0, 'sys:audit:delete',    3, NULL,                    NULL,                             NULL,                    1, 0, 0, '{"zh-CN":"清理日志","zh-TW":"清理日誌","en-US":"Purge Logs","ja-JP":"ログ削除"}'::jsonb),
  (35, '个人信息',   '/profile',     0, 99, 0, 'profile:view',        2, 'IdcardOutlined',       'views/ProfileView.vue',         'ProfileView',           0, 0, 0, '{"zh-CN":"个人信息","zh-TW":"個人資訊","en-US":"My Profile","ja-JP":"個人情報"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- 7b. Roles
INSERT INTO sys_role (role_id, role_name, role_code, description, sort_order, status)
VALUES
  (1, '超级管理员', 'super_admin', '拥有全部权限，不可删除', 1, 'active'),
  (2, '系统管理员', 'admin',       '可管理用户/角色/菜单/字典与审计日志', 2, 'active'),
  (3, '调度操作员', 'operator',    '日常仓储作业与设备控制', 3, 'active'),
  (4, '只读访客',   'viewer',      '仅可查看控制台与孪生视图', 4, 'active')
ON CONFLICT (role_id) DO NOTHING;

-- 7c. Users (default password "rcs@2026" -> bcrypt hash below)
INSERT INTO sys_user (user_id, username, password_hash, real_name, email, phone, is_admin, status)
VALUES
  (1, 'admin',    '$2b$12$RftCjOqsEqH0UnM/jTpNMewCiwT76E6V.IZ6Ls/JzTiJxLBDXBIjK', '系统管理员', 'admin@rcs.local',    NULL, TRUE,  'active'),
  (2, 'operator', '$2b$12$RftCjOqsEqH0UnM/jTpNMewCiwT76E6V.IZ6Ls/JzTiJxLBDXBIjK', '调度操作员', 'operator@rcs.local', NULL, FALSE, 'active'),
  (3, 'viewer',   '$2b$12$RftCjOqsEqH0UnM/jTpNMewCiwT76E6V.IZ6Ls/JzTiJxLBDXBIjK', '只读访客',   'viewer@rcs.local',   NULL, FALSE, 'active')
ON CONFLICT (user_id) DO NOTHING;

-- 7d. Role -> Menu grants
INSERT INTO sys_role_menu (role_id, menu_id)
VALUES
  -- super_admin / admin: every remaining menu (*)
  (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,13),(1,14),
  (1,15),(1,16),(1,17),(1,18),(1,19),(1,20),(1,21),(1,22),(1,23),(1,24),(1,25),(1,26),(1,27),
  (1,28),(1,29),(1,30),(1,31),(1,32),(1,33),(1,34),(1,35),
  (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(2,13),(2,14),
  (2,15),(2,16),(2,17),(2,18),(2,19),(2,20),(2,21),(2,22),(2,23),(2,24),(2,25),(2,26),(2,27),
  (2,28),(2,29),(2,30),(2,31),(2,32),(2,33),(2,34),(2,35),
  -- operator: devices / wms + profile
  (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,35),
  -- viewer: dashboard + profile
  (4,1),(4,35)
ON CONFLICT (role_id, menu_id) DO NOTHING;

-- 7e. User -> Role grants
INSERT INTO sys_user_role (user_id, role_id)
VALUES
  (1, 1),   -- admin    -> super_admin
  (2, 3),   -- operator -> operator
  (3, 4)    -- viewer   -> viewer
ON CONFLICT (user_id, role_id) DO NOTHING;

-- 7f. Advance serial sequences so the app keeps auto-issuing ids past the seed rows.
SELECT setval(pg_get_serial_sequence('sys_menu',       'id'),       (SELECT COALESCE(MAX(id), 1)       FROM sys_menu));
SELECT setval(pg_get_serial_sequence('sys_role',       'role_id'),  (SELECT COALESCE(MAX(role_id), 1) FROM sys_role));
SELECT setval(pg_get_serial_sequence('sys_user',       'user_id'),  (SELECT COALESCE(MAX(user_id), 1) FROM sys_user));
SELECT setval(pg_get_serial_sequence('sys_role_menu',  'id'),       (SELECT COALESCE(MAX(id), 1)       FROM sys_role_menu));
SELECT setval(pg_get_serial_sequence('sys_user_role',  'id'),       (SELECT COALESCE(MAX(id), 1)       FROM sys_user_role));

-- 8. Scene-map scenario templates
-- 13 init scene-map templates (7 canonical primary rows match Python
-- SCENARIO_IDS; 6 secondary variants are SQL-only presets). Idempotent.
INSERT INTO robot_unified_maps (
    map_id, name, name_en, is_template, kind, current_version,
    bounds_json, geometry_json, topology_json, semantic_json,
    dynamic_json, data
)
VALUES
    ('tpl-ecommerce', '大型电商仓库', 'Large E-commerce Warehouse', TRUE, 'scenario', 1, '{"w": 120, "d": 80}'::json, '{"bounds": {"w": 120, "d": 80}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 120, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 78, "w": 120, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 80, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 118, "z": 0, "w": 2, "d": 80, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "dock-01", "type": "truck_dock", "x": 0, "z": 12, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卸货口1"}, {"ref": "dock-02", "type": "truck_dock", "x": 0, "z": 26, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卸货口2"}, {"ref": "dock-03", "type": "truck_dock", "x": 0, "z": 40, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卸货口3"}, {"ref": "dock-04", "type": "truck_dock", "x": 118, "z": 12, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "装货口1"}, {"ref": "dock-05", "type": "truck_dock", "x": 118, "z": 26, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "装货口2"}, {"ref": "dock-06", "type": "truck_dock", "x": 118, "z": 40, "w": 2, "d": 6, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "装货口3"}], "facilities": [{"ref": "office", "type": "office", "x": 104, "z": 4, "w": 12, "d": 10, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#a855f7", "label": "办公区"}], "zones": [{"ref": "stg-rcv", "type": "receiving", "x": 10, "z": 4, "w": 14, "d": 16, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "收货暂存"}, {"ref": "stg-ship", "type": "shipping", "x": 10, "z": 58, "w": 14, "d": 18, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "发货暂存"}, {"ref": "pick-a", "type": "flow_rack", "x": 30, "z": 6, "w": 34, "d": 22, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#f59e0b", "label": "流利货架A"}, {"ref": "pick-b", "type": "flow_rack", "x": 30, "z": 34, "w": 34, "d": 22, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#f59e0b", "label": "流利货架B"}, {"ref": "pick-c", "type": "flow_rack", "x": 30, "z": 62, "w": 34, "d": 16, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#f59e0b", "label": "流利货架C"}, {"ref": "rack-h1", "type": "high_rack", "x": 70, "z": 6, "w": 40, "d": 22, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#d97706", "label": "高位货架1"}, {"ref": "rack-h2", "type": "high_rack", "x": 70, "z": 34, "w": 40, "d": 22, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#d97706", "label": "高位货架2"}, {"ref": "rack-h3", "type": "high_rack", "x": 70, "z": 62, "w": 40, "d": 16, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#d97706", "label": "高位货架3"}, {"ref": "mezz", "type": "mezzanine", "x": 4, "z": 4, "w": 4, "d": 30, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#a16207", "label": "夹层办公"}, {"ref": "asrs", "type": "asrs", "x": 4, "z": 40, "w": 4, "d": 30, "h": 8.0, "y": 0.0, "rot": 0.0, "color": "#0ea5e9", "label": "自动立库"}, {"ref": "ret", "type": "returns", "x": 26, "z": 4, "w": 4, "d": 8, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#ef4444", "label": "退货区"}], "corridors": [{"ref": "main-aisle", "type": "corridor", "x": 10, "z": 30, "w": 100, "d": 6, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "主通道"}, {"ref": "cross-aisle", "type": "corridor", "x": 64, "z": 4, "w": 6, "d": 72, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "横向通道"}]}'::json, '{}'::json, '{"scenario": "ecommerce", "variant": "A1", "reference": "warehouse_theatre_3d/docs/superpowers/specs/2026-08-18-ecommerce-warehouse-zones-design.md §4 DEFAULT_SHELL"}'::json, '{}'::json, '{}'::json),
    ('tpl-train_unload', '火车卸货→月台→大卡车(单线)', 'Rail Unload → Platform → Truck (single siding)', TRUE, 'scenario', 1, '{"w": 180, "d": 80}'::json, '{"bounds": {"w": 180, "d": 80}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 180, "d": 2, "h": 7, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 78, "w": 180, "d": 2, "h": 7, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 80, "h": 7, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 178, "z": 0, "w": 2, "d": 80, "h": 7, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "truck-dock-1", "type": "truck_dock", "x": 76, "z": 12, "w": 2, "d": 12, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卡车月台1"}, {"ref": "truck-dock-2", "type": "truck_dock", "x": 76, "z": 30, "w": 2, "d": 12, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卡车月台2"}, {"ref": "truck-dock-3", "type": "truck_dock", "x": 76, "z": 48, "w": 2, "d": 12, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "卡车月台3"}], "facilities": [], "zones": [{"ref": "rail-track-1", "type": "rail_track", "x": 0, "z": 10, "w": 10, "d": 60, "h": 0.3, "y": 0.0, "rot": 0.0, "color": "#44403c", "label": "铁路侧线"}, {"ref": "train-car-1", "type": "train_car", "x": 12, "z": 12, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车1"}, {"ref": "train-car-2", "type": "train_car", "x": 12, "z": 30, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车2"}, {"ref": "train-car-3", "type": "train_car", "x": 12, "z": 48, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车3"}, {"ref": "platform", "type": "platform", "x": 30, "z": 8, "w": 24, "d": 64, "h": 1.2, "y": 0.3, "rot": 0.0, "color": "#eab308", "label": "转运月台"}, {"ref": "truck-1", "type": "truck", "x": 60, "z": 12, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "大卡车1"}, {"ref": "truck-2", "type": "truck", "x": 60, "z": 30, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "大卡车2"}, {"ref": "truck-3", "type": "truck", "x": 60, "z": 48, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "大卡车3"}, {"ref": "staging", "type": "staging", "x": 90, "z": 8, "w": 88, "d": 64, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#94a3b8", "label": "暂存/分拣区"}, {"ref": "qc", "type": "qc_staging", "x": 100, "z": 10, "w": 20, "d": 20, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "质检分拣"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 30, "z": 4, "w": 120, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "作业通道"}]}'::json, '{}'::json, '{"scenario": "rail_unload", "variant": "B1", "reference": "BNSF 50ft Boxcar Diagram; Rite-Hite 标准月台高 4ft(1.219m)", "flow": ["rail_track", "train_car", "platform", "truck"]}'::json, '{}'::json, '{}'::json),
    ('tpl-train_unload-1', '火车卸货→月台→大卡车(双线多式联运)', 'Rail Unload → Platform → Truck (twin siding ICD)', TRUE, 'scenario', 1, '{"w": 220, "d": 90}'::json, '{"bounds": {"w": 220, "d": 90}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 220, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 88, "w": 220, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 90, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 218, "z": 0, "w": 2, "d": 90, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [], "facilities": [], "zones": [{"ref": "rail-track-1", "type": "rail_track", "x": 0, "z": 10, "w": 10, "d": 70, "h": 0.3, "y": 0.0, "rot": 0.0, "color": "#44403c", "label": "铁路一线"}, {"ref": "rail-track-2", "type": "rail_track", "x": 14, "z": 10, "w": 10, "d": 70, "h": 0.3, "y": 0.0, "rot": 0.0, "color": "#44403c", "label": "铁路二线"}, {"ref": "train-car-1", "type": "train_car", "x": 0, "z": 14, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车1-1"}, {"ref": "train-car-2", "type": "train_car", "x": 0, "z": 32, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车1-2"}, {"ref": "train-car-3", "type": "train_car", "x": 0, "z": 50, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车1-3"}, {"ref": "train-car-4", "type": "train_car", "x": 14, "z": 14, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车2-1"}, {"ref": "train-car-5", "type": "train_car", "x": 14, "z": 32, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车2-2"}, {"ref": "train-car-6", "type": "train_car", "x": 14, "z": 50, "w": 15, "d": 12, "h": 4.0, "y": 0.0, "rot": 0.0, "color": "#7c2d12", "label": "棚车2-3"}, {"ref": "platform-1", "type": "platform", "x": 30, "z": 8, "w": 22, "d": 74, "h": 1.2, "y": 0.3, "rot": 0.0, "color": "#eab308", "label": "北侧月台"}, {"ref": "platform-2", "type": "platform", "x": 110, "z": 8, "w": 22, "d": 74, "h": 1.2, "y": 0.3, "rot": 0.0, "color": "#eab308", "label": "南侧月台"}, {"ref": "truck-1", "type": "truck", "x": 56, "z": 14, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车1"}, {"ref": "truck-2", "type": "truck", "x": 56, "z": 32, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车2"}, {"ref": "truck-3", "type": "truck", "x": 56, "z": 50, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车3"}, {"ref": "truck-4", "type": "truck", "x": 136, "z": 14, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车4"}, {"ref": "truck-5", "type": "truck", "x": 136, "z": 32, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车5"}, {"ref": "truck-6", "type": "truck", "x": 136, "z": 50, "w": 14, "d": 12, "h": 3.5, "y": 0.0, "rot": 0.0, "color": "#1f2937", "label": "卡车6"}, {"ref": "staging-1", "type": "staging", "x": 78, "z": 8, "w": 28, "d": 74, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#94a3b8", "label": "中区暂存"}, {"ref": "staging-2", "type": "staging", "x": 158, "z": 8, "w": 60, "d": 74, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#94a3b8", "label": "出库暂存"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 30, "z": 4, "w": 160, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "作业通道"}]}'::json, '{}'::json, '{"scenario": "rail_unload", "variant": "B2", "reference": "BNSF 50/60ft Boxcar; Rite-Hite 月台 1.219m; 集装箱多式联运场站惯例", "flow": ["rail_track", "train_car", "platform", "truck"]}'::json, '{}'::json, '{}'::json),
    ('tpl-manufacturing', '工厂仓库(含卸货)-离散制造', 'Factory Warehouse w/ Unloading (discrete mfg)', TRUE, 'scenario', 1, '{"w": 100, "d": 80}'::json, '{"bounds": {"w": 100, "d": 80}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 100, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 78, "w": 100, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 80, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 98, "z": 0, "w": 2, "d": 80, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "rcv-dock-1", "type": "truck_dock", "x": 0, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "收货月台1"}, {"ref": "rcv-dock-2", "type": "truck_dock", "x": 0, "z": 26, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "收货月台2"}, {"ref": "ship-dock-1", "type": "truck_dock", "x": 98, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "发运月台1"}, {"ref": "ship-dock-2", "type": "truck_dock", "x": 98, "z": 26, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "发运月台2"}], "facilities": [{"ref": "office", "type": "office", "x": 86, "z": 50, "w": 10, "d": 12, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#a855f7", "label": "厂务办公"}], "zones": [{"ref": "stg-rcv", "type": "receiving", "x": 8, "z": 8, "w": 16, "d": 30, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "收货暂存"}, {"ref": "line-1", "type": "production_line", "x": 30, "z": 8, "w": 30, "d": 14, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#64748b", "label": "生产线1"}, {"ref": "line-2", "type": "production_line", "x": 30, "z": 26, "w": 30, "d": 14, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#64748b", "label": "生产线2"}, {"ref": "wip-1", "type": "wip_buffer", "x": 30, "z": 44, "w": 18, "d": 12, "h": 1.0, "y": 0.0, "rot": 0.0, "color": "#475569", "label": "WIP缓冲1"}, {"ref": "wip-2", "type": "wip_buffer", "x": 30, "z": 60, "w": 18, "d": 12, "h": 1.0, "y": 0.0, "rot": 0.0, "color": "#475569", "label": "WIP缓冲2"}, {"ref": "parts", "type": "parts_storage", "x": 54, "z": 8, "w": 24, "d": 34, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#334155", "label": "零部件库"}, {"ref": "stg-ship", "type": "shipping", "x": 64, "z": 8, "w": 32, "d": 30, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "成品暂存"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 8, "z": 44, "w": 84, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "物流通道"}]}'::json, '{}'::json, '{"scenario": "manufacturing", "variant": "C1", "reference": "离散制造仓通用布局; 收货/发运月台高≈1.2m(Rite-Hite)"}'::json, '{}'::json, '{}'::json),
    ('tpl-manufacturing-1', '工厂仓库(含卸货)-流水线大产线', 'Factory Warehouse w/ Unloading (flow line)', TRUE, 'scenario', 1, '{"w": 120, "d": 90}'::json, '{"bounds": {"w": 120, "d": 90}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 120, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 88, "w": 120, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 90, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 118, "z": 0, "w": 2, "d": 90, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "rcv-dock-1", "type": "truck_dock", "x": 0, "z": 12, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "收货月台1"}, {"ref": "rcv-dock-2", "type": "truck_dock", "x": 0, "z": 28, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "收货月台2"}, {"ref": "rcv-dock-3", "type": "truck_dock", "x": 0, "z": 44, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "收货月台3"}, {"ref": "ship-dock-1", "type": "truck_dock", "x": 118, "z": 12, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "发运月台1"}, {"ref": "ship-dock-2", "type": "truck_dock", "x": 118, "z": 28, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "发运月台2"}], "facilities": [{"ref": "office", "type": "office", "x": 106, "z": 60, "w": 10, "d": 14, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#a855f7", "label": "厂务办公"}], "zones": [{"ref": "stg-rcv", "type": "receiving", "x": 8, "z": 8, "w": 18, "d": 40, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "收货暂存"}, {"ref": "line-1", "type": "production_line", "x": 32, "z": 8, "w": 40, "d": 16, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#64748b", "label": "主线1"}, {"ref": "line-2", "type": "production_line", "x": 32, "z": 28, "w": 40, "d": 16, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#64748b", "label": "主线2"}, {"ref": "line-3", "type": "production_line", "x": 32, "z": 48, "w": 40, "d": 16, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#64748b", "label": "主线3"}, {"ref": "wip-1", "type": "wip_buffer", "x": 32, "z": 68, "w": 24, "d": 14, "h": 1.0, "y": 0.0, "rot": 0.0, "color": "#475569", "label": "WIP缓冲"}, {"ref": "parts", "type": "parts_storage", "x": 76, "z": 8, "w": 26, "d": 40, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#334155", "label": "零部件库"}, {"ref": "fin-rack", "type": "high_rack", "x": 76, "z": 52, "w": 26, "d": 30, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#d97706", "label": "成品高架"}, {"ref": "stg-ship", "type": "shipping", "x": 78, "z": 8, "w": 30, "d": 30, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "成品暂存"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 8, "z": 52, "w": 100, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "物流通道"}]}'::json, '{}'::json, '{"scenario": "manufacturing", "variant": "C2", "reference": "汽车/家电总装厂物流布局惯例; 月台 1.2m"}'::json, '{}'::json, '{}'::json),
    ('tpl-port', '港口码头卸货-集装箱堆场', 'Port Terminal Unloading (container yard)', TRUE, 'scenario', 1, '{"w": 200, "d": 150}'::json, '{"bounds": {"w": 200, "d": 150}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 200, "d": 2, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 148, "w": 200, "d": 2, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 150, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 198, "z": 0, "w": 2, "d": 150, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "quay", "type": "ship_dock", "x": 0, "z": 0, "w": 12, "d": 30, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#0ea5e9", "label": "码头岸线"}, {"ref": "gate", "type": "truck_dock", "x": 198, "z": 40, "w": 2, "d": 20, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "闸口发运"}], "facilities": [], "zones": [{"ref": "crane-apron", "type": "corridor", "x": 12, "z": 0, "w": 30, "d": 30, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "岸桥作业带"}, {"ref": "customs", "type": "customs_area", "x": 12, "z": 34, "w": 40, "d": 24, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#8b5cf6", "label": "海关查验区"}, {"ref": "yard-a-0-0", "type": "container_yard", "x": 60.0, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-0"}, {"ref": "yard-a-0-1", "type": "container_yard", "x": 62.74, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-1"}, {"ref": "yard-a-0-2", "type": "container_yard", "x": 65.48, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-2"}, {"ref": "yard-a-0-3", "type": "container_yard", "x": 68.22, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-3"}, {"ref": "yard-a-0-4", "type": "container_yard", "x": 70.96, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-4"}, {"ref": "yard-a-0-5", "type": "container_yard", "x": 73.7, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-5"}, {"ref": "yard-a-0-6", "type": "container_yard", "x": 76.44, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-6"}, {"ref": "yard-a-1-0", "type": "container_yard", "x": 60.0, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-0"}, {"ref": "yard-a-1-1", "type": "container_yard", "x": 62.74, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-1"}, {"ref": "yard-a-1-2", "type": "container_yard", "x": 65.48, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-2"}, {"ref": "yard-a-1-3", "type": "container_yard", "x": 68.22, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-3"}, {"ref": "yard-a-1-4", "type": "container_yard", "x": 70.96, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-4"}, {"ref": "yard-a-1-5", "type": "container_yard", "x": 73.7, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-5"}, {"ref": "yard-a-1-6", "type": "container_yard", "x": 76.44, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-6"}, {"ref": "yard-a-2-0", "type": "container_yard", "x": 60.0, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-0"}, {"ref": "yard-a-2-1", "type": "container_yard", "x": 62.74, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-1"}, {"ref": "yard-a-2-2", "type": "container_yard", "x": 65.48, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-2"}, {"ref": "yard-a-2-3", "type": "container_yard", "x": 68.22, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-3"}, {"ref": "yard-a-2-4", "type": "container_yard", "x": 70.96, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-4"}, {"ref": "yard-a-2-5", "type": "container_yard", "x": 73.7, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-5"}, {"ref": "yard-a-2-6", "type": "container_yard", "x": 76.44, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-6"}, {"ref": "yard-a-3-0", "type": "container_yard", "x": 60.0, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-0"}, {"ref": "yard-a-3-1", "type": "container_yard", "x": 62.74, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-1"}, {"ref": "yard-a-3-2", "type": "container_yard", "x": 65.48, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-2"}, {"ref": "yard-a-3-3", "type": "container_yard", "x": 68.22, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-3"}, {"ref": "yard-a-3-4", "type": "container_yard", "x": 70.96, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-4"}, {"ref": "yard-a-3-5", "type": "container_yard", "x": 73.7, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-5"}, {"ref": "yard-a-3-6", "type": "container_yard", "x": 76.44, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-6"}, {"ref": "yard-a-4-0", "type": "container_yard", "x": 60.0, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-0"}, {"ref": "yard-a-4-1", "type": "container_yard", "x": 62.74, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-1"}, {"ref": "yard-a-4-2", "type": "container_yard", "x": 65.48, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-2"}, {"ref": "yard-a-4-3", "type": "container_yard", "x": 68.22, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-3"}, {"ref": "yard-a-4-4", "type": "container_yard", "x": 70.96, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-4"}, {"ref": "yard-a-4-5", "type": "container_yard", "x": 73.7, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-5"}, {"ref": "yard-a-4-6", "type": "container_yard", "x": 76.44, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-6"}, {"ref": "yard-a-5-0", "type": "container_yard", "x": 60.0, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-0"}, {"ref": "yard-a-5-1", "type": "container_yard", "x": 62.74, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-1"}, {"ref": "yard-a-5-2", "type": "container_yard", "x": 65.48, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-2"}, {"ref": "yard-a-5-3", "type": "container_yard", "x": 68.22, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-3"}, {"ref": "yard-a-5-4", "type": "container_yard", "x": 70.96, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-4"}, {"ref": "yard-a-5-5", "type": "container_yard", "x": 73.7, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-5"}, {"ref": "yard-a-5-6", "type": "container_yard", "x": 76.44, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-6"}, {"ref": "yard-b-0-0", "type": "container_yard", "x": 130.0, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-0"}, {"ref": "yard-b-0-1", "type": "container_yard", "x": 132.74, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-1"}, {"ref": "yard-b-0-2", "type": "container_yard", "x": 135.48, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-2"}, {"ref": "yard-b-0-3", "type": "container_yard", "x": 138.22, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-3"}, {"ref": "yard-b-0-4", "type": "container_yard", "x": 140.96, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-4"}, {"ref": "yard-b-0-5", "type": "container_yard", "x": 143.7, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-5"}, {"ref": "yard-b-0-6", "type": "container_yard", "x": 146.44, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-6"}, {"ref": "yard-b-1-0", "type": "container_yard", "x": 130.0, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-0"}, {"ref": "yard-b-1-1", "type": "container_yard", "x": 132.74, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-1"}, {"ref": "yard-b-1-2", "type": "container_yard", "x": 135.48, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-2"}, {"ref": "yard-b-1-3", "type": "container_yard", "x": 138.22, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-3"}, {"ref": "yard-b-1-4", "type": "container_yard", "x": 140.96, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-4"}, {"ref": "yard-b-1-5", "type": "container_yard", "x": 143.7, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-5"}, {"ref": "yard-b-1-6", "type": "container_yard", "x": 146.44, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-6"}, {"ref": "yard-b-2-0", "type": "container_yard", "x": 130.0, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-0"}, {"ref": "yard-b-2-1", "type": "container_yard", "x": 132.74, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-1"}, {"ref": "yard-b-2-2", "type": "container_yard", "x": 135.48, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-2"}, {"ref": "yard-b-2-3", "type": "container_yard", "x": 138.22, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-3"}, {"ref": "yard-b-2-4", "type": "container_yard", "x": 140.96, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-4"}, {"ref": "yard-b-2-5", "type": "container_yard", "x": 143.7, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-5"}, {"ref": "yard-b-2-6", "type": "container_yard", "x": 146.44, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-6"}, {"ref": "yard-b-3-0", "type": "container_yard", "x": 130.0, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-0"}, {"ref": "yard-b-3-1", "type": "container_yard", "x": 132.74, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-1"}, {"ref": "yard-b-3-2", "type": "container_yard", "x": 135.48, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-2"}, {"ref": "yard-b-3-3", "type": "container_yard", "x": 138.22, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-3"}, {"ref": "yard-b-3-4", "type": "container_yard", "x": 140.96, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-4"}, {"ref": "yard-b-3-5", "type": "container_yard", "x": 143.7, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-5"}, {"ref": "yard-b-3-6", "type": "container_yard", "x": 146.44, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-6"}, {"ref": "yard-b-4-0", "type": "container_yard", "x": 130.0, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-0"}, {"ref": "yard-b-4-1", "type": "container_yard", "x": 132.74, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-1"}, {"ref": "yard-b-4-2", "type": "container_yard", "x": 135.48, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-2"}, {"ref": "yard-b-4-3", "type": "container_yard", "x": 138.22, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-3"}, {"ref": "yard-b-4-4", "type": "container_yard", "x": 140.96, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-4"}, {"ref": "yard-b-4-5", "type": "container_yard", "x": 143.7, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-5"}, {"ref": "yard-b-4-6", "type": "container_yard", "x": 146.44, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-6"}, {"ref": "yard-b-5-0", "type": "container_yard", "x": 130.0, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-0"}, {"ref": "yard-b-5-1", "type": "container_yard", "x": 132.74, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-1"}, {"ref": "yard-b-5-2", "type": "container_yard", "x": 135.48, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-2"}, {"ref": "yard-b-5-3", "type": "container_yard", "x": 138.22, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-3"}, {"ref": "yard-b-5-4", "type": "container_yard", "x": 140.96, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-4"}, {"ref": "yard-b-5-5", "type": "container_yard", "x": 143.7, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-5"}, {"ref": "yard-b-5-6", "type": "container_yard", "x": 146.44, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-6"}, {"ref": "reefer", "type": "cold_zone", "x": 60, "z": 60, "w": 60, "d": 20, "h": 2.9, "y": 0.0, "rot": 0.0, "color": "#60a5fa", "label": "冷藏箱区"}, {"ref": "staging", "type": "staging", "x": 60, "z": 90, "w": 120, "d": 50, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#94a3b8", "label": "中转暂存"}], "corridors": [{"ref": "apron", "type": "corridor", "x": 12, "z": 30, "w": 180, "d": 6, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "水平运输通道"}]}'::json, '{}'::json, '{"scenario": "port", "variant": "D1", "reference": "Container 20ft 6.06×2.44×2.59m / 40ft 12.19×2.44×2.59m (kscranegroup,hansatic); 堆场 6–7 列(porteconomicsmanagement Ch6.5)"}'::json, '{}'::json, '{}'::json),
    ('tpl-port-1', '港口码头卸货-多泊位', 'Port Terminal Unloading (multi-berth)', TRUE, 'scenario', 1, '{"w": 240, "d": 160}'::json, '{"bounds": {"w": 240, "d": 160}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 240, "d": 2, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 158, "w": 240, "d": 2, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 160, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 238, "z": 0, "w": 2, "d": 160, "h": 4, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "quay-1", "type": "ship_dock", "x": 0, "z": 0, "w": 12, "d": 40, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#0ea5e9", "label": "泊位1岸线"}, {"ref": "quay-2", "type": "ship_dock", "x": 0, "z": 50, "w": 12, "d": 40, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#0ea5e9", "label": "泊位2岸线"}, {"ref": "gate", "type": "truck_dock", "x": 238, "z": 60, "w": 2, "d": 30, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "闸口"}], "facilities": [], "zones": [{"ref": "crane-apron", "type": "corridor", "x": 12, "z": 0, "w": 34, "d": 100, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "岸桥作业带"}, {"ref": "customs", "type": "customs_area", "x": 12, "z": 110, "w": 50, "d": 30, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#8b5cf6", "label": "海关查验区"}, {"ref": "yard-a-0-0", "type": "container_yard", "x": 70.0, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-0"}, {"ref": "yard-a-0-1", "type": "container_yard", "x": 72.74, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-1"}, {"ref": "yard-a-0-2", "type": "container_yard", "x": 75.48, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-2"}, {"ref": "yard-a-0-3", "type": "container_yard", "x": 78.22, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-3"}, {"ref": "yard-a-0-4", "type": "container_yard", "x": 80.96, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-4"}, {"ref": "yard-a-0-5", "type": "container_yard", "x": 83.7, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-5"}, {"ref": "yard-a-0-6", "type": "container_yard", "x": 86.44, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-6"}, {"ref": "yard-a-0-7", "type": "container_yard", "x": 89.18, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-7"}, {"ref": "yard-a-1-0", "type": "container_yard", "x": 70.0, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-0"}, {"ref": "yard-a-1-1", "type": "container_yard", "x": 72.74, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-1"}, {"ref": "yard-a-1-2", "type": "container_yard", "x": 75.48, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-2"}, {"ref": "yard-a-1-3", "type": "container_yard", "x": 78.22, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-3"}, {"ref": "yard-a-1-4", "type": "container_yard", "x": 80.96, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-4"}, {"ref": "yard-a-1-5", "type": "container_yard", "x": 83.7, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-5"}, {"ref": "yard-a-1-6", "type": "container_yard", "x": 86.44, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-6"}, {"ref": "yard-a-1-7", "type": "container_yard", "x": 89.18, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-7"}, {"ref": "yard-a-2-0", "type": "container_yard", "x": 70.0, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-0"}, {"ref": "yard-a-2-1", "type": "container_yard", "x": 72.74, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-1"}, {"ref": "yard-a-2-2", "type": "container_yard", "x": 75.48, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-2"}, {"ref": "yard-a-2-3", "type": "container_yard", "x": 78.22, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-3"}, {"ref": "yard-a-2-4", "type": "container_yard", "x": 80.96, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-4"}, {"ref": "yard-a-2-5", "type": "container_yard", "x": 83.7, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-5"}, {"ref": "yard-a-2-6", "type": "container_yard", "x": 86.44, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-6"}, {"ref": "yard-a-2-7", "type": "container_yard", "x": 89.18, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-7"}, {"ref": "yard-a-3-0", "type": "container_yard", "x": 70.0, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-0"}, {"ref": "yard-a-3-1", "type": "container_yard", "x": 72.74, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-1"}, {"ref": "yard-a-3-2", "type": "container_yard", "x": 75.48, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-2"}, {"ref": "yard-a-3-3", "type": "container_yard", "x": 78.22, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-3"}, {"ref": "yard-a-3-4", "type": "container_yard", "x": 80.96, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-4"}, {"ref": "yard-a-3-5", "type": "container_yard", "x": 83.7, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-5"}, {"ref": "yard-a-3-6", "type": "container_yard", "x": 86.44, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-6"}, {"ref": "yard-a-3-7", "type": "container_yard", "x": 89.18, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-7"}, {"ref": "yard-a-4-0", "type": "container_yard", "x": 70.0, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-0"}, {"ref": "yard-a-4-1", "type": "container_yard", "x": 72.74, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-1"}, {"ref": "yard-a-4-2", "type": "container_yard", "x": 75.48, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-2"}, {"ref": "yard-a-4-3", "type": "container_yard", "x": 78.22, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-3"}, {"ref": "yard-a-4-4", "type": "container_yard", "x": 80.96, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-4"}, {"ref": "yard-a-4-5", "type": "container_yard", "x": 83.7, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-5"}, {"ref": "yard-a-4-6", "type": "container_yard", "x": 86.44, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-6"}, {"ref": "yard-a-4-7", "type": "container_yard", "x": 89.18, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-7"}, {"ref": "yard-a-5-0", "type": "container_yard", "x": 70.0, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-0"}, {"ref": "yard-a-5-1", "type": "container_yard", "x": 72.74, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-1"}, {"ref": "yard-a-5-2", "type": "container_yard", "x": 75.48, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-2"}, {"ref": "yard-a-5-3", "type": "container_yard", "x": 78.22, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-3"}, {"ref": "yard-a-5-4", "type": "container_yard", "x": 80.96, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-4"}, {"ref": "yard-a-5-5", "type": "container_yard", "x": 83.7, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-5"}, {"ref": "yard-a-5-6", "type": "container_yard", "x": 86.44, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-6"}, {"ref": "yard-a-5-7", "type": "container_yard", "x": 89.18, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-7"}, {"ref": "yard-a-6-0", "type": "container_yard", "x": 70.0, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-0"}, {"ref": "yard-a-6-1", "type": "container_yard", "x": 72.74, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-1"}, {"ref": "yard-a-6-2", "type": "container_yard", "x": 75.48, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-2"}, {"ref": "yard-a-6-3", "type": "container_yard", "x": 78.22, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-3"}, {"ref": "yard-a-6-4", "type": "container_yard", "x": 80.96, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-4"}, {"ref": "yard-a-6-5", "type": "container_yard", "x": 83.7, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-5"}, {"ref": "yard-a-6-6", "type": "container_yard", "x": 86.44, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-6"}, {"ref": "yard-a-6-7", "type": "container_yard", "x": 89.18, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-7"}, {"ref": "yard-b-0-0", "type": "container_yard", "x": 150.0, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-0"}, {"ref": "yard-b-0-1", "type": "container_yard", "x": 152.74, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-1"}, {"ref": "yard-b-0-2", "type": "container_yard", "x": 155.48, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-2"}, {"ref": "yard-b-0-3", "type": "container_yard", "x": 158.22, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-3"}, {"ref": "yard-b-0-4", "type": "container_yard", "x": 160.96, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-4"}, {"ref": "yard-b-0-5", "type": "container_yard", "x": 163.7, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-5"}, {"ref": "yard-b-0-6", "type": "container_yard", "x": 166.44, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-6"}, {"ref": "yard-b-0-7", "type": "container_yard", "x": 169.18, "z": 10.0, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱0-7"}, {"ref": "yard-b-1-0", "type": "container_yard", "x": 150.0, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-0"}, {"ref": "yard-b-1-1", "type": "container_yard", "x": 152.74, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-1"}, {"ref": "yard-b-1-2", "type": "container_yard", "x": 155.48, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-2"}, {"ref": "yard-b-1-3", "type": "container_yard", "x": 158.22, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-3"}, {"ref": "yard-b-1-4", "type": "container_yard", "x": 160.96, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-4"}, {"ref": "yard-b-1-5", "type": "container_yard", "x": 163.7, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-5"}, {"ref": "yard-b-1-6", "type": "container_yard", "x": 166.44, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-6"}, {"ref": "yard-b-1-7", "type": "container_yard", "x": 169.18, "z": 16.36, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱1-7"}, {"ref": "yard-b-2-0", "type": "container_yard", "x": 150.0, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-0"}, {"ref": "yard-b-2-1", "type": "container_yard", "x": 152.74, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-1"}, {"ref": "yard-b-2-2", "type": "container_yard", "x": 155.48, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-2"}, {"ref": "yard-b-2-3", "type": "container_yard", "x": 158.22, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-3"}, {"ref": "yard-b-2-4", "type": "container_yard", "x": 160.96, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-4"}, {"ref": "yard-b-2-5", "type": "container_yard", "x": 163.7, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-5"}, {"ref": "yard-b-2-6", "type": "container_yard", "x": 166.44, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-6"}, {"ref": "yard-b-2-7", "type": "container_yard", "x": 169.18, "z": 22.72, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱2-7"}, {"ref": "yard-b-3-0", "type": "container_yard", "x": 150.0, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-0"}, {"ref": "yard-b-3-1", "type": "container_yard", "x": 152.74, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-1"}, {"ref": "yard-b-3-2", "type": "container_yard", "x": 155.48, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-2"}, {"ref": "yard-b-3-3", "type": "container_yard", "x": 158.22, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-3"}, {"ref": "yard-b-3-4", "type": "container_yard", "x": 160.96, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-4"}, {"ref": "yard-b-3-5", "type": "container_yard", "x": 163.7, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-5"}, {"ref": "yard-b-3-6", "type": "container_yard", "x": 166.44, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-6"}, {"ref": "yard-b-3-7", "type": "container_yard", "x": 169.18, "z": 29.08, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱3-7"}, {"ref": "yard-b-4-0", "type": "container_yard", "x": 150.0, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-0"}, {"ref": "yard-b-4-1", "type": "container_yard", "x": 152.74, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-1"}, {"ref": "yard-b-4-2", "type": "container_yard", "x": 155.48, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-2"}, {"ref": "yard-b-4-3", "type": "container_yard", "x": 158.22, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-3"}, {"ref": "yard-b-4-4", "type": "container_yard", "x": 160.96, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-4"}, {"ref": "yard-b-4-5", "type": "container_yard", "x": 163.7, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-5"}, {"ref": "yard-b-4-6", "type": "container_yard", "x": 166.44, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-6"}, {"ref": "yard-b-4-7", "type": "container_yard", "x": 169.18, "z": 35.44, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱4-7"}, {"ref": "yard-b-5-0", "type": "container_yard", "x": 150.0, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-0"}, {"ref": "yard-b-5-1", "type": "container_yard", "x": 152.74, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-1"}, {"ref": "yard-b-5-2", "type": "container_yard", "x": 155.48, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-2"}, {"ref": "yard-b-5-3", "type": "container_yard", "x": 158.22, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-3"}, {"ref": "yard-b-5-4", "type": "container_yard", "x": 160.96, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-4"}, {"ref": "yard-b-5-5", "type": "container_yard", "x": 163.7, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-5"}, {"ref": "yard-b-5-6", "type": "container_yard", "x": 166.44, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-6"}, {"ref": "yard-b-5-7", "type": "container_yard", "x": 169.18, "z": 41.8, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱5-7"}, {"ref": "yard-b-6-0", "type": "container_yard", "x": 150.0, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-0"}, {"ref": "yard-b-6-1", "type": "container_yard", "x": 152.74, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-1"}, {"ref": "yard-b-6-2", "type": "container_yard", "x": 155.48, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-2"}, {"ref": "yard-b-6-3", "type": "container_yard", "x": 158.22, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-3"}, {"ref": "yard-b-6-4", "type": "container_yard", "x": 160.96, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-4"}, {"ref": "yard-b-6-5", "type": "container_yard", "x": 163.7, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-5"}, {"ref": "yard-b-6-6", "type": "container_yard", "x": 166.44, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-6"}, {"ref": "yard-b-6-7", "type": "container_yard", "x": 169.18, "z": 48.16, "w": 2.44, "d": 6.06, "h": 2.59, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "箱6-7"}, {"ref": "reefer", "type": "cold_zone", "x": 70, "z": 70, "w": 70, "d": 24, "h": 2.9, "y": 0.0, "rot": 0.0, "color": "#60a5fa", "label": "冷藏箱区"}, {"ref": "empty-yard", "type": "container_yard", "x": 150, "z": 70, "w": 70, "d": 24, "h": 0.3, "y": 0.0, "rot": 0.0, "color": "#10b981", "label": "空箱堆场"}, {"ref": "staging", "type": "staging", "x": 70, "z": 100, "w": 150, "d": 50, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#94a3b8", "label": "中转暂存"}], "corridors": [{"ref": "apron", "type": "corridor", "x": 12, "z": 100, "w": 220, "d": 6, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "水平运输通道"}]}'::json, '{}'::json, '{"scenario": "port", "variant": "D2", "reference": "ISO 集装箱尺寸; 多泊位集装箱码头布局(porteconomicsmanagement Ch6.5)"}'::json, '{}'::json, '{}'::json),
    ('tpl-scn-cold_chain', '冷链仓库-冷冻+冷藏+穿堂', 'Cold Chain (frozen+chilled+airlock)', TRUE, 'scenario', 1, '{"w": 80, "d": 60, "h": 8}'::json, '{"bounds": {"w": 80, "d": 60, "h": 8}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 80, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 58, "w": 80, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 60, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 78, "z": 0, "w": 2, "d": 60, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "dock-1", "type": "truck_dock", "x": 0, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "冷藏月台1"}, {"ref": "dock-2", "type": "truck_dock", "x": 0, "z": 26, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "冷藏月台2"}], "facilities": [], "zones": [{"ref": "airlock", "type": "ambient_zone", "x": 8, "z": 10, "w": 10, "d": 24, "h": 5.0, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "穿堂/缓冲"}, {"ref": "frozen", "type": "frozen_zone", "x": 22, "z": 8, "w": 30, "d": 30, "h": 6, "y": 0.0, "rot": 0.0, "color": "#3b82f6", "label": "冷冻区(-18℃)"}, {"ref": "chilled", "type": "cold_zone", "x": 22, "z": 40, "w": 30, "d": 18, "h": 6, "y": 0.0, "rot": 0.0, "color": "#60a5fa", "label": "冷藏区(2~4℃)"}, {"ref": "ambient", "type": "ambient_zone", "x": 56, "z": 8, "w": 20, "d": 40, "h": 5, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "常温暂存"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 8, "z": 36, "w": 64, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "内通道"}]}'::json, '{}'::json, '{"scenario": "cold_chain", "variant": "E1", "reference": "GCCA/IE Cold Storage: Frozen -10°F(-23℃)/Chilled 34°F(1℃); 冷链月台需密封门封"}'::json, '{}'::json, '{}'::json),
    ('tpl-scn-cold_chain-1', '冷链仓库-深冷+预冷+分拣', 'Cold Chain (deep-freeze+precool+sort)', TRUE, 'scenario', 1, '{"w": 100, "d": 70, "h": 9}'::json, '{"bounds": {"w": 100, "d": 70, "h": 9}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 100, "d": 2, "h": 9, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 68, "w": 100, "d": 2, "h": 9, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 70, "h": 9, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 98, "z": 0, "w": 2, "d": 70, "h": 9, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "dock-1", "type": "truck_dock", "x": 0, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "冷藏月台1"}, {"ref": "dock-2", "type": "truck_dock", "x": 0, "z": 24, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "冷藏月台2"}, {"ref": "dock-3", "type": "truck_dock", "x": 0, "z": 38, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "冷藏月台3"}], "facilities": [], "zones": [{"ref": "precool", "type": "cold_zone", "x": 8, "z": 10, "w": 12, "d": 24, "h": 5, "y": 0.0, "rot": 0.0, "color": "#60a5fa", "label": "快速预冷(0~4℃)"}, {"ref": "airlock", "type": "ambient_zone", "x": 8, "z": 36, "w": 12, "d": 24, "h": 5.0, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "穿堂"}, {"ref": "frozen", "type": "frozen_zone", "x": 24, "z": 8, "w": 36, "d": 28, "h": 7, "y": 0.0, "rot": 0.0, "color": "#3b82f6", "label": "冷冻区(-22℃)"}, {"ref": "chilled", "type": "cold_zone", "x": 24, "z": 40, "w": 36, "d": 24, "h": 7, "y": 0.0, "rot": 0.0, "color": "#60a5fa", "label": "冷藏区(2~8℃)"}, {"ref": "ambient", "type": "ambient_zone", "x": 64, "z": 8, "w": 32, "d": 50, "h": 5, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "常温/分拣"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 8, "z": 62, "w": 84, "d": 4, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "内通道"}]}'::json, '{}'::json, '{"scenario": "cold_chain", "variant": "E2", "reference": "GCCA 冷藏设计; 冷冻 -18~-25℃ 区间; 生鲜冷藏 1~8℃"}'::json, '{}'::json, '{}'::json),
    ('tpl-scn-reverse_logistics', '退货异常仓库-标准逆向', 'Reverse Logistics (standard returns)', TRUE, 'scenario', 1, '{"w": 60, "d": 40}'::json, '{"bounds": {"w": 60, "d": 40}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 60, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 38, "w": 60, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 40, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 58, "z": 0, "w": 2, "d": 40, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "rcv-dock", "type": "truck_dock", "x": 0, "z": 12, "w": 2, "d": 10, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "退货卸货口"}], "facilities": [], "zones": [{"ref": "rcv", "type": "returns_received", "x": 6, "z": 8, "w": 14, "d": 24, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#ef4444", "label": "退货接收"}, {"ref": "inspect", "type": "qc_staging", "x": 24, "z": 8, "w": 14, "d": 12, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "质检分级"}, {"ref": "sort", "type": "qc_staging", "x": 24, "z": 24, "w": 14, "d": 12, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "分拣归类"}, {"ref": "quarantine", "type": "returns", "x": 42, "z": 8, "w": 14, "d": 12, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#ef4444", "label": "隔离待决"}, {"ref": "refurb", "type": "reshelving", "x": 42, "z": 24, "w": 14, "d": 12, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#fca5a5", "label": "翻修/再上架"}, {"ref": "dispose", "type": "disposal", "x": 6, "z": 34, "w": 20, "d": 6, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#dc2626", "label": "残损处置"}, {"ref": "ship", "type": "shipping", "x": 40, "z": 34, "w": 18, "d": 6, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "正向出库"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 6, "z": 36, "w": 50, "d": 2, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "作业通道"}]}'::json, '{}'::json, '{"scenario": "reverse_logistics", "variant": "F1", "reference": "ReturnPro 逆向中心分区; ShelvingIndia 退货仓布局(接收/质检/分拣/隔离/翻修/处置)"}'::json, '{}'::json, '{}'::json),
    ('tpl-scn-reverse_logistics-1', '退货异常仓库-高退货量电商', 'Reverse Logistics (high-volume e-com)', TRUE, 'scenario', 1, '{"w": 80, "d": 50}'::json, '{"bounds": {"w": 80, "d": 50}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 80, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 48, "w": 80, "d": 2, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 50, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 78, "z": 0, "w": 2, "d": 50, "h": 6.0, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "rcv-dock-1", "type": "truck_dock", "x": 0, "z": 10, "w": 2, "d": 10, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "退货卸货1"}, {"ref": "rcv-dock-2", "type": "truck_dock", "x": 0, "z": 26, "w": 2, "d": 10, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "退货卸货2"}], "facilities": [], "zones": [{"ref": "rcv", "type": "returns_received", "x": 6, "z": 8, "w": 18, "d": 30, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#ef4444", "label": "大批量退货接收"}, {"ref": "inspect-1", "type": "qc_staging", "x": 28, "z": 8, "w": 16, "d": 14, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "质检分级1"}, {"ref": "inspect-2", "type": "qc_staging", "x": 28, "z": 26, "w": 16, "d": 14, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "质检分级2"}, {"ref": "sort", "type": "qc_staging", "x": 48, "z": 8, "w": 14, "d": 14, "h": 1.5, "y": 0.0, "rot": 0.0, "color": "#f87171", "label": "自动分拣"}, {"ref": "quarantine", "type": "returns", "x": 48, "z": 26, "w": 14, "d": 14, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#ef4444", "label": "隔离待决"}, {"ref": "refurb-1", "type": "reshelving", "x": 66, "z": 8, "w": 12, "d": 14, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#fca5a5", "label": "翻修工位1"}, {"ref": "refurb-2", "type": "reshelving", "x": 66, "z": 26, "w": 12, "d": 14, "h": 3.0, "y": 0.0, "rot": 0.0, "color": "#fca5a5", "label": "翻修工位2"}, {"ref": "dispose", "type": "disposal", "x": 6, "z": 40, "w": 24, "d": 8, "h": 2.0, "y": 0.0, "rot": 0.0, "color": "#dc2626", "label": "残损处置"}, {"ref": "ship", "type": "shipping", "x": 36, "z": 40, "w": 42, "d": 8, "h": 0.6, "y": 0.0, "rot": 0.0, "color": "#cbd5e1", "label": "正向/转售出库"}], "corridors": [{"ref": "aisle", "type": "corridor", "x": 6, "z": 42, "w": 70, "d": 2, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "作业通道"}]}'::json, '{}'::json, '{"scenario": "reverse_logistics", "variant": "F2", "reference": "NRF 退货率逐年攀升; Pallite 电商退货处理区设计; ReturnPro 分区"}'::json, '{}'::json, '{}'::json),
    ('tpl-multi_floor', '多层仓库-3层(收/拣/存)', 'Multi-floor Warehouse (3 levels)', TRUE, 'scenario', 1, '{"w": 80, "d": 60, "h": 12}'::json, '{"bounds": {"w": 80, "d": 60, "h": 12}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 80, "d": 2, "h": 12, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 58, "w": 80, "d": 2, "h": 12, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 60, "h": 12, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 78, "z": 0, "w": 2, "d": 60, "h": 12, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "dock-1", "type": "truck_dock", "x": 0, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "L1卸货口"}, {"ref": "dock-2", "type": "truck_dock", "x": 78, "z": 10, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "L1装货口"}], "facilities": [], "zones": [{"ref": "floor-1-rcv", "type": "floor_1", "x": 6, "z": 6, "w": 30, "d": 20, "h": 4, "y": 0, "rot": 0.0, "color": "#64748b", "label": "L1收货暂存"}, {"ref": "floor-1-stage", "type": "floor_1", "x": 6, "z": 30, "w": 30, "d": 20, "h": 4, "y": 0, "rot": 0.0, "color": "#64748b", "label": "L1发货暂存"}, {"ref": "floor-2-pick", "type": "floor_2", "x": 6, "z": 6, "w": 30, "d": 40, "h": 4, "y": 4, "rot": 0.0, "color": "#475569", "label": "L2拣选区"}, {"ref": "floor-3-store", "type": "floor_3", "x": 6, "z": 6, "w": 30, "d": 40, "h": 4, "y": 8, "rot": 0.0, "color": "#334155", "label": "L3存储区"}, {"ref": "elevator", "type": "elevator_shaft", "x": 40, "z": 6, "w": 6, "d": 6, "h": 12, "y": 0, "rot": 0.0, "color": "#22d3ee", "label": "货梯/垂直输送"}], "floors": [{"level": 1, "y": 0, "zones": ["floor-1-rcv", "floor-1-stage"]}, {"level": 2, "y": 4, "zones": ["floor-2-pick"]}, {"level": 3, "y": 8, "zones": ["floor-3-store"]}], "corridors": [{"ref": "core", "type": "corridor", "x": 40, "z": 12, "w": 6, "d": 40, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "核心筒通道"}]}'::json, '{}'::json, '{"scenario": "multi_floor", "variant": "G1", "reference": "GSE Group 多层物流建筑(每层专用); X-YES/GS 垂直输送机/货梯连接楼层"}'::json, '{}'::json, '{}'::json),
    ('tpl-multi_floor-1', '多层仓库-2层(储发/拣办)', 'Multi-floor Warehouse (2 levels)', TRUE, 'scenario', 1, '{"w": 90, "d": 70, "h": 8}'::json, '{"bounds": {"w": 90, "d": 70, "h": 8}, "walls": [{"ref": "wall-n", "type": "perimeter", "x": 0, "z": 0, "w": 90, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "北墙"}, {"ref": "wall-s", "type": "perimeter", "x": 0, "z": 68, "w": 90, "d": 2, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "南墙"}, {"ref": "wall-w", "type": "perimeter", "x": 0, "z": 0, "w": 2, "d": 70, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "西墙"}, {"ref": "wall-e", "type": "perimeter", "x": 88, "z": 0, "w": 2, "d": 70, "h": 8, "y": 0.0, "rot": 0.0, "color": "#6b7280", "label": "东墙"}], "docks": [{"ref": "dock-1", "type": "truck_dock", "x": 0, "z": 12, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "L1卸货口"}, {"ref": "dock-2", "type": "truck_dock", "x": 0, "z": 28, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "L1卸货口2"}, {"ref": "dock-3", "type": "truck_dock", "x": 88, "z": 12, "w": 2, "d": 8, "h": 1.2, "y": 0.0, "rot": 0.0, "color": "#fbbf24", "label": "L1装货口"}], "facilities": [], "zones": [{"ref": "floor-1-store", "type": "floor_1", "x": 6, "z": 6, "w": 36, "d": 30, "h": 4, "y": 0, "rot": 0.0, "color": "#64748b", "label": "L1存储/发货"}, {"ref": "floor-1-ship", "type": "floor_1", "x": 6, "z": 40, "w": 36, "d": 20, "h": 4, "y": 0, "rot": 0.0, "color": "#64748b", "label": "L1发货暂存"}, {"ref": "floor-2-pick", "type": "floor_2", "x": 6, "z": 6, "w": 36, "d": 30, "h": 4, "y": 4, "rot": 0.0, "color": "#475569", "label": "L2拣选"}, {"ref": "floor-2-office", "type": "floor_2", "x": 6, "z": 40, "w": 36, "d": 20, "h": 4, "y": 4, "rot": 0.0, "color": "#475569", "label": "L2办公/质控"}, {"ref": "elevator", "type": "elevator_shaft", "x": 46, "z": 6, "w": 8, "d": 8, "h": 12, "y": 0, "rot": 0.0, "color": "#22d3ee", "label": "自动垂直输送"}], "floors": [{"level": 1, "y": 0, "zones": ["floor-1-store", "floor-1-ship"]}, {"level": 2, "y": 4, "zones": ["floor-2-pick", "floor-2-office"]}], "corridors": [{"ref": "core", "type": "corridor", "x": 46, "z": 16, "w": 8, "d": 40, "h": 0.0, "y": 0.0, "rot": 0.0, "color": "#e5e7eb", "label": "核心筒通道"}]}'::json, '{}'::json, '{"scenario": "multi_floor", "variant": "G2", "reference": "多层配送中心惯例; 垂直输送机(gssort)/货梯连接楼层"}'::json, '{}'::json, '{}'::json)
ON CONFLICT (map_id) DO UPDATE SET
    name = EXCLUDED.name,
    name_en = EXCLUDED.name_en,
    is_template = EXCLUDED.is_template,
    kind = EXCLUDED.kind,
    current_version = EXCLUDED.current_version,
    bounds_json = EXCLUDED.bounds_json,
    geometry_json = EXCLUDED.geometry_json,
    topology_json = EXCLUDED.topology_json,
    semantic_json = EXCLUDED.semantic_json,
    dynamic_json = EXCLUDED.dynamic_json,
    data = EXCLUDED.data;
