-- RCS Backend — PostgreSQL schema (v1)
-- Apply with:  psql "$DATABASE_URL" -f migrations/001_init.sql
-- or let the app auto-create tables on startup (init_db) when storage=postgres.

CREATE TABLE IF NOT EXISTS devices (
    device_id           TEXT PRIMARY KEY,
    morphology          TEXT NOT NULL,
    robot_type          TEXT,
    num_joints          INTEGER NOT NULL DEFAULT 0,
    control_hz          INTEGER NOT NULL DEFAULT 0,
    mode                TEXT,
    active_command_id   TEXT,
    last_error          TEXT,
    locked              BOOLEAN NOT NULL DEFAULT FALSE,
    base_pose_in_world  JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    order_id            TEXT PRIMARY KEY,
    scenario_id         TEXT,
    priority            INTEGER NOT NULL DEFAULT 5,
    deadline            DOUBLE PRECISION,
    status              TEXT NOT NULL DEFAULT 'queued',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_orders_scenario_id ON orders (scenario_id);
CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status);

CREATE TABLE IF NOT EXISTS order_items (
    id                  BIGSERIAL PRIMARY KEY,
    order_id            TEXT NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    ref                 TEXT NOT NULL,
    quantity            INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items (order_id);

CREATE TABLE IF NOT EXISTS order_tasks (
    id                  BIGSERIAL PRIMARY KEY,
    order_id            TEXT NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    node_id             TEXT NOT NULL,
    task_type           TEXT NOT NULL,
    slo_class           TEXT NOT NULL,
    depends_on          JSONB NOT NULL DEFAULT '[]',
    status              TEXT NOT NULL DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS ix_order_tasks_order_id ON order_tasks (order_id);
CREATE INDEX IF NOT EXISTS ix_order_tasks_status ON order_tasks (status);
CREATE UNIQUE INDEX IF NOT EXISTS uq_order_task ON order_tasks (order_id, node_id);

CREATE TABLE IF NOT EXISTS topology_shell (
    site_id             TEXT PRIMARY KEY,
    name                TEXT,
    width_m             DOUBLE PRECISION NOT NULL DEFAULT 0,
    depth_m             DOUBLE PRECISION NOT NULL DEFAULT 0,
    height_m            DOUBLE PRECISION NOT NULL DEFAULT 0,
    data                JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS topology_grid (
    id                  BIGSERIAL PRIMARY KEY,
    site_id             TEXT NOT NULL REFERENCES topology_shell (site_id) ON DELETE CASCADE,
    zone_id             TEXT NOT NULL,
    zone_type           INTEGER NOT NULL DEFAULT 0,
    center_m            JSONB NOT NULL DEFAULT '[]',
    size_m              JSONB NOT NULL DEFAULT '[]',
    rotation_deg        DOUBLE PRECISION NOT NULL DEFAULT 0,
    data                JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_topology_grid_site_id ON topology_grid (site_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_zone ON topology_grid (site_id, zone_id);
