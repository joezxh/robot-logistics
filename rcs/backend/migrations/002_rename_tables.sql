-- RCS Backend — migration v2: prefix existing tables with `robot_`
-- Apply with:  psql "$DATABASE_URL" -f migrations/002_rename_tables.sql
--
-- Renames the six v1 tables created by 001_init.sql (before the prefix
-- convention was introduced) so they match the ORM __tablename__ values
-- and newly created databases.
--
-- Idempotent & safe to re-run: each rename only fires when the OLD (unprefixed)
-- table still exists and the NEW (prefixed) one does not. PostgreSQL lacks
-- ALTER TABLE IF EXISTS, so we use a DO block with dynamic SQL.
--
-- PostgreSQL automatically updates foreign-key references when a table is
-- renamed, so the FKs on order_items / order_tasks / topology_grid keep
-- pointing at the renamed parent tables.

DO $$
BEGIN
    -- devices -> robot_devices
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='devices')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_devices') THEN
        EXECUTE 'ALTER TABLE devices RENAME TO robot_devices';
    END IF;

    -- orders -> robot_orders (parent of order_items / order_tasks FKs)
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='orders')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_orders') THEN
        EXECUTE 'ALTER TABLE orders RENAME TO robot_orders';
    END IF;

    -- order_items -> robot_order_items
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='order_items')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_order_items') THEN
        EXECUTE 'ALTER TABLE order_items RENAME TO robot_order_items';
    END IF;

    -- order_tasks -> robot_order_tasks
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='order_tasks')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_order_tasks') THEN
        EXECUTE 'ALTER TABLE order_tasks RENAME TO robot_order_tasks';
    END IF;

    -- topology_shell -> robot_topology_shell (parent of topology_grid FK)
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='topology_shell')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_topology_shell') THEN
        EXECUTE 'ALTER TABLE topology_shell RENAME TO robot_topology_shell';
    END IF;

    -- topology_grid -> robot_topology_grid
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='topology_grid')
       AND NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='robot_topology_grid') THEN
        EXECUTE 'ALTER TABLE topology_grid RENAME TO robot_topology_grid';
    END IF;

    -- Rename unique constraints to the new naming convention so a fresh
    -- create_all / 001_init.sql run does not error on duplicate constraint
    -- names. (Constraint names are per-table, so this is optional but keeps
    -- schemas consistent across environments.)
    IF EXISTS (SELECT 1 FROM pg_constraint c
               JOIN pg_class t ON t.oid = c.conrelid
               WHERE t.relname='robot_order_tasks' AND c.conname='uq_order_task') THEN
        EXECUTE 'ALTER TABLE robot_order_tasks RENAME CONSTRAINT uq_order_task TO robot_uq_order_task';
    END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint c
               JOIN pg_class t ON t.oid = c.conrelid
               WHERE t.relname='robot_topology_grid' AND c.conname='uq_zone') THEN
        EXECUTE 'ALTER TABLE robot_topology_grid RENAME CONSTRAINT uq_zone TO robot_uq_zone';
    END IF;
END $$;
