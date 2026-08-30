/*
 Navicat Premium Dump SQL

 Source Server         : pgvector-localhost
 Source Server Type    : PostgreSQL
 Source Server Version : 180004 (180004)
 Source Host           : localhost:5432
 Source Catalog        : rcs
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 180004 (180004)
 File Encoding         : 65001

 Date: 30/08/2026 00:07:03
*/


-- ----------------------------
-- Table structure for sys_audit_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_audit_log";
CREATE TABLE "public"."sys_audit_log" (
  "log_id" int8 NOT NULL DEFAULT nextval('sys_audit_log_log_id_seq'::regclass),
  "user_id" int8,
  "username" varchar(50) COLLATE "pg_catalog"."default",
  "operation_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "operation_module" varchar(50) COLLATE "pg_catalog"."default",
  "operation_desc" text COLLATE "pg_catalog"."default",
  "request_method" varchar(10) COLLATE "pg_catalog"."default",
  "request_url" varchar(500) COLLATE "pg_catalog"."default",
  "request_params" jsonb,
  "request_ip" varchar(50) COLLATE "pg_catalog"."default",
  "user_agent" varchar(500) COLLATE "pg_catalog"."default",
  "response_status" int4,
  "response_time_ms" int4,
  "old_data" jsonb,
  "new_data" jsonb,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_audit_log"."log_id" IS '日志ID';
COMMENT ON COLUMN "public"."sys_audit_log"."user_id" IS '用户ID';
COMMENT ON COLUMN "public"."sys_audit_log"."username" IS '用户名';
COMMENT ON COLUMN "public"."sys_audit_log"."operation_type" IS '操作类型：create-创建, update-更新, delete-删除, query-查询, login-登录, logout-登出';
COMMENT ON COLUMN "public"."sys_audit_log"."operation_module" IS '操作模块';
COMMENT ON COLUMN "public"."sys_audit_log"."operation_desc" IS '操作描述';
COMMENT ON COLUMN "public"."sys_audit_log"."request_method" IS '请求方法';
COMMENT ON COLUMN "public"."sys_audit_log"."request_url" IS '请求URL';
COMMENT ON COLUMN "public"."sys_audit_log"."request_params" IS '请求参数';
COMMENT ON COLUMN "public"."sys_audit_log"."request_ip" IS '请求IP';
COMMENT ON COLUMN "public"."sys_audit_log"."user_agent" IS '用户代理';
COMMENT ON COLUMN "public"."sys_audit_log"."response_status" IS '响应状态码';
COMMENT ON COLUMN "public"."sys_audit_log"."response_time_ms" IS '响应时间(毫秒)';
COMMENT ON COLUMN "public"."sys_audit_log"."old_data" IS '旧数据';
COMMENT ON COLUMN "public"."sys_audit_log"."new_data" IS '新数据';
COMMENT ON COLUMN "public"."sys_audit_log"."created_at" IS '创建时间';
COMMENT ON TABLE "public"."sys_audit_log" IS '系统审计日志表';

-- ----------------------------
-- Table structure for sys_dictionary
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_dictionary";
CREATE TABLE "public"."sys_dictionary" (
  "dict_id" int8 NOT NULL DEFAULT nextval('sys_dictionary_dict_id_seq'::regclass),
  "dict_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "dict_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "dict_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "sort_order" int4 DEFAULT 0,
  "is_active" bool NOT NULL DEFAULT true,
  "extra_data" jsonb,
  "created_by" int8,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool NOT NULL DEFAULT false
)
;
COMMENT ON COLUMN "public"."sys_dictionary"."dict_id" IS '字典ID';
COMMENT ON COLUMN "public"."sys_dictionary"."dict_code" IS '字典编码';
COMMENT ON COLUMN "public"."sys_dictionary"."dict_name" IS '字典名称';
COMMENT ON COLUMN "public"."sys_dictionary"."dict_type" IS '字典类型';
COMMENT ON COLUMN "public"."sys_dictionary"."description" IS '字典描述';
COMMENT ON COLUMN "public"."sys_dictionary"."sort_order" IS '排序顺序';
COMMENT ON COLUMN "public"."sys_dictionary"."is_active" IS '是否启用';
COMMENT ON COLUMN "public"."sys_dictionary"."extra_data" IS '扩展数据';
COMMENT ON TABLE "public"."sys_dictionary" IS '系统字典表';

-- ----------------------------
-- Table structure for sys_dictionary_item
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_dictionary_item";
CREATE TABLE "public"."sys_dictionary_item" (
  "item_id" int8 NOT NULL DEFAULT nextval('sys_dictionary_item_item_id_seq'::regclass),
  "dict_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "item_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "item_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "item_value" varchar(200) COLLATE "pg_catalog"."default",
  "parent_code" varchar(50) COLLATE "pg_catalog"."default",
  "level" int4 DEFAULT 1,
  "color" varchar(20) COLLATE "pg_catalog"."default",
  "icon" varchar(50) COLLATE "pg_catalog"."default",
  "sort_order" int4 DEFAULT 0,
  "is_active" bool NOT NULL DEFAULT true,
  "extra_data" jsonb,
  "remark" text COLLATE "pg_catalog"."default",
  "created_by" int8,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool NOT NULL DEFAULT false
)
;
COMMENT ON COLUMN "public"."sys_dictionary_item"."item_id" IS '字典项ID';
COMMENT ON COLUMN "public"."sys_dictionary_item"."dict_code" IS '所属字典编码';
COMMENT ON COLUMN "public"."sys_dictionary_item"."item_code" IS '字典项编码';
COMMENT ON COLUMN "public"."sys_dictionary_item"."item_name" IS '字典项名称';
COMMENT ON COLUMN "public"."sys_dictionary_item"."item_value" IS '字典项值';
COMMENT ON COLUMN "public"."sys_dictionary_item"."parent_code" IS '父级编码';
COMMENT ON COLUMN "public"."sys_dictionary_item"."level" IS '层级';
COMMENT ON COLUMN "public"."sys_dictionary_item"."color" IS '颜色标识';
COMMENT ON COLUMN "public"."sys_dictionary_item"."icon" IS '图标';
COMMENT ON COLUMN "public"."sys_dictionary_item"."sort_order" IS '排序顺序';
COMMENT ON COLUMN "public"."sys_dictionary_item"."is_active" IS '是否启用';
COMMENT ON COLUMN "public"."sys_dictionary_item"."extra_data" IS '扩展数据';
COMMENT ON COLUMN "public"."sys_dictionary_item"."remark" IS '备注';
COMMENT ON TABLE "public"."sys_dictionary_item" IS '系统字典项表';

-- ----------------------------
-- Table structure for sys_menu
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_menu";
CREATE TABLE "public"."sys_menu" (
  "id" int8 NOT NULL DEFAULT nextval('sys_permission_permission_id_seq'::regclass),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "path" varchar(255) COLLATE "pg_catalog"."default",
  "parent_id" int8,
  "sort" int4 DEFAULT 0,
  "status" int4 DEFAULT 0,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "permission" varchar(100) COLLATE "pg_catalog"."default",
  "type" int4 DEFAULT 2,
  "icon" varchar(100) COLLATE "pg_catalog"."default",
  "component" varchar(255) COLLATE "pg_catalog"."default",
  "is_deleted" bool DEFAULT false,
  "component_name" varchar(100) COLLATE "pg_catalog"."default",
  "visible" int4 DEFAULT 1,
  "keep_alive" int4 DEFAULT 0,
  "always_show" int4 DEFAULT 0
)
;
COMMENT ON COLUMN "public"."sys_menu"."id" IS '权限ID';
COMMENT ON COLUMN "public"."sys_menu"."name" IS '权限名称';
COMMENT ON COLUMN "public"."sys_menu"."path" IS '路由地址';
COMMENT ON COLUMN "public"."sys_menu"."parent_id" IS '父权限ID';
COMMENT ON COLUMN "public"."sys_menu"."sort" IS '显示顺序';
COMMENT ON COLUMN "public"."sys_menu"."status" IS '状态: 0=开启, 1=关闭';
COMMENT ON COLUMN "public"."sys_menu"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_menu"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."sys_menu"."component" IS '前端组件路径';
COMMENT ON COLUMN "public"."sys_menu"."component_name" IS '组件名称';
COMMENT ON COLUMN "public"."sys_menu"."visible" IS '是否可见: 1=显示, 0=隐藏';
COMMENT ON COLUMN "public"."sys_menu"."keep_alive" IS '是否缓存: 1=缓存, 0=不缓存';
COMMENT ON COLUMN "public"."sys_menu"."always_show" IS '是否总是显示: 1=总是, 0=不是';
COMMENT ON TABLE "public"."sys_menu" IS '权限表';

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_role";
CREATE TABLE "public"."sys_role" (
  "role_id" int8 NOT NULL DEFAULT nextval('sys_role_role_id_seq'::regclass),
  "role_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "role_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "region_code" varchar(20) COLLATE "pg_catalog"."default",
  "region_level" varchar(20) COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default",
  "sort_order" int4 DEFAULT 0,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'active'::character varying,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool NOT NULL DEFAULT false
)
;
COMMENT ON COLUMN "public"."sys_role"."role_id" IS '角色ID';
COMMENT ON COLUMN "public"."sys_role"."role_name" IS '角色名称';
COMMENT ON COLUMN "public"."sys_role"."role_code" IS '角色编码';
COMMENT ON COLUMN "public"."sys_role"."region_code" IS '区域编码';
COMMENT ON COLUMN "public"."sys_role"."region_level" IS '地区层级：province-省, city-市, district-区县, street-街道';
COMMENT ON COLUMN "public"."sys_role"."description" IS '描述';
COMMENT ON COLUMN "public"."sys_role"."sort_order" IS '排序';
COMMENT ON COLUMN "public"."sys_role"."status" IS '状态';
COMMENT ON COLUMN "public"."sys_role"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_role"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."sys_role"."is_deleted" IS '是否删除';
COMMENT ON TABLE "public"."sys_role" IS '系统角色表，角色与地区权限绑定';

-- ----------------------------
-- Table structure for sys_role_menu
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_role_menu";
CREATE TABLE "public"."sys_role_menu" (
  "id" int8 NOT NULL DEFAULT nextval('sys_role_permission_id_seq'::regclass),
  "role_id" int8 NOT NULL,
  "menu_id" int8 NOT NULL,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_role_menu"."id" IS '关联ID';
COMMENT ON COLUMN "public"."sys_role_menu"."role_id" IS '角色ID';
COMMENT ON COLUMN "public"."sys_role_menu"."menu_id" IS '权限ID';
COMMENT ON COLUMN "public"."sys_role_menu"."created_at" IS '创建时间';
COMMENT ON TABLE "public"."sys_role_menu" IS '角色权限关联表';

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_user";
CREATE TABLE "public"."sys_user" (
  "user_id" int8 NOT NULL DEFAULT nextval('sys_user_user_id_seq'::regclass),
  "username" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "password_hash" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "real_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "phone" varchar(20) COLLATE "pg_catalog"."default",
  "email" varchar(100) COLLATE "pg_catalog"."default",
  "avatar_url" varchar(500) COLLATE "pg_catalog"."default",
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'active'::character varying,
  "is_admin" bool NOT NULL DEFAULT false,
  "last_login_at" timestamp(6),
  "last_login_ip" varchar(50) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "deleted_at" timestamp(6),
  "is_deleted" bool NOT NULL DEFAULT false
)
;
COMMENT ON COLUMN "public"."sys_user"."user_id" IS '用户ID';
COMMENT ON COLUMN "public"."sys_user"."username" IS '登录账号';
COMMENT ON COLUMN "public"."sys_user"."password_hash" IS '密码哈希（bcrypt）';
COMMENT ON COLUMN "public"."sys_user"."real_name" IS '真实姓名';
COMMENT ON COLUMN "public"."sys_user"."phone" IS '手机号';
COMMENT ON COLUMN "public"."sys_user"."email" IS '邮箱';
COMMENT ON COLUMN "public"."sys_user"."avatar_url" IS '头像URL';
COMMENT ON COLUMN "public"."sys_user"."status" IS '状态：active-启用, disabled-禁用';
COMMENT ON COLUMN "public"."sys_user"."is_admin" IS '是否管理员';
COMMENT ON COLUMN "public"."sys_user"."last_login_at" IS '最后登录时间';
COMMENT ON COLUMN "public"."sys_user"."last_login_ip" IS '最后登录IP';
COMMENT ON COLUMN "public"."sys_user"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_user"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."sys_user"."deleted_at" IS '删除时间';
COMMENT ON COLUMN "public"."sys_user"."is_deleted" IS '是否删除';
COMMENT ON TABLE "public"."sys_user" IS '系统用户表';

-- ----------------------------
-- Table structure for sys_user_role
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_user_role";
CREATE TABLE "public"."sys_user_role" (
  "id" int8 NOT NULL DEFAULT nextval('sys_user_role_id_seq'::regclass),
  "user_id" int8 NOT NULL,
  "role_id" int8 NOT NULL,
  "created_at" timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_user_role"."id" IS '关联ID';
COMMENT ON COLUMN "public"."sys_user_role"."user_id" IS '用户ID';
COMMENT ON COLUMN "public"."sys_user_role"."role_id" IS '角色ID';
COMMENT ON COLUMN "public"."sys_user_role"."created_at" IS '创建时间';
COMMENT ON TABLE "public"."sys_user_role" IS '用户角色关联表';

-- ----------------------------
-- Indexes structure for table sys_audit_log
-- ----------------------------
CREATE INDEX "idx_audit_ip" ON "public"."sys_audit_log" USING btree (
  "request_ip" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_audit_operation" ON "public"."sys_audit_log" USING btree (
  "operation_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "operation_module" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_audit_time" ON "public"."sys_audit_log" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_audit_user" ON "public"."sys_audit_log" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sys_audit_log_created_at" ON "public"."sys_audit_log" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sys_audit_log_request_ip" ON "public"."sys_audit_log" USING btree (
  "request_ip" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sys_audit_log_user_id" ON "public"."sys_audit_log" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sys_audit_log
-- ----------------------------
ALTER TABLE "public"."sys_audit_log" ADD CONSTRAINT "sys_audit_log_pkey" PRIMARY KEY ("log_id");

-- ----------------------------
-- Indexes structure for table sys_dictionary
-- ----------------------------
CREATE INDEX "idx_dict_active" ON "public"."sys_dictionary" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_dict_code" ON "public"."sys_dictionary" USING btree (
  "dict_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_dict_type" ON "public"."sys_dictionary" USING btree (
  "dict_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;

-- ----------------------------
-- Uniques structure for table sys_dictionary
-- ----------------------------
ALTER TABLE "public"."sys_dictionary" ADD CONSTRAINT "sys_dictionary_dict_code_key" UNIQUE ("dict_code");

-- ----------------------------
-- Primary Key structure for table sys_dictionary
-- ----------------------------
ALTER TABLE "public"."sys_dictionary" ADD CONSTRAINT "sys_dictionary_pkey" PRIMARY KEY ("dict_id");

-- ----------------------------
-- Indexes structure for table sys_dictionary_item
-- ----------------------------
CREATE INDEX "idx_dict_item_code_order" ON "public"."sys_dictionary_item" USING btree (
  "dict_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "sort_order" "pg_catalog"."int4_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_item_active" ON "public"."sys_dictionary_item" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_item_code" ON "public"."sys_dictionary_item" USING btree (
  "item_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_item_dict_code" ON "public"."sys_dictionary_item" USING btree (
  "dict_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_item_parent" ON "public"."sys_dictionary_item" USING btree (
  "parent_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;

-- ----------------------------
-- Uniques structure for table sys_dictionary_item
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_item" ADD CONSTRAINT "sys_dictionary_item_dict_code_item_code_key" UNIQUE ("dict_code", "item_code");

-- ----------------------------
-- Primary Key structure for table sys_dictionary_item
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_item" ADD CONSTRAINT "sys_dictionary_item_pkey" PRIMARY KEY ("item_id");

-- ----------------------------
-- Indexes structure for table sys_menu
-- ----------------------------
CREATE INDEX "idx_menu_parent_id" ON "public"."sys_menu" USING btree (
  "parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_menu_status" ON "public"."sys_menu" USING btree (
  "status" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "idx_menu_type" ON "public"."sys_menu" USING btree (
  "type" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sys_menu_parent_id" ON "public"."sys_menu" USING btree (
  "parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sys_menu
-- ----------------------------
ALTER TABLE "public"."sys_menu" ADD CONSTRAINT "sys_menu_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sys_role
-- ----------------------------
CREATE INDEX "idx_role_code" ON "public"."sys_role" USING btree (
  "role_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_role_region" ON "public"."sys_role" USING btree (
  "region_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;

-- ----------------------------
-- Uniques structure for table sys_role
-- ----------------------------
ALTER TABLE "public"."sys_role" ADD CONSTRAINT "sys_role_role_code_key" UNIQUE ("role_code");

-- ----------------------------
-- Primary Key structure for table sys_role
-- ----------------------------
ALTER TABLE "public"."sys_role" ADD CONSTRAINT "sys_role_pkey" PRIMARY KEY ("role_id");

-- ----------------------------
-- Indexes structure for table sys_role_menu
-- ----------------------------
CREATE INDEX "idx_role_menu_menu_id" ON "public"."sys_role_menu" USING btree (
  "menu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_role_menu_role_id" ON "public"."sys_role_menu" USING btree (
  "role_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sys_role_menu
-- ----------------------------
ALTER TABLE "public"."sys_role_menu" ADD CONSTRAINT "sys_role_permission_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sys_user
-- ----------------------------
CREATE INDEX "idx_user_status" ON "public"."sys_user" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE INDEX "idx_user_username" ON "public"."sys_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE is_deleted = false;
CREATE UNIQUE INDEX "ix_sys_user_username" ON "public"."sys_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table sys_user
-- ----------------------------
ALTER TABLE "public"."sys_user" ADD CONSTRAINT "sys_user_username_key" UNIQUE ("username");

-- ----------------------------
-- Primary Key structure for table sys_user
-- ----------------------------
ALTER TABLE "public"."sys_user" ADD CONSTRAINT "sys_user_pkey" PRIMARY KEY ("user_id");

-- ----------------------------
-- Indexes structure for table sys_user_role
-- ----------------------------
CREATE INDEX "idx_user_role_role" ON "public"."sys_user_role" USING btree (
  "role_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_user_role_user" ON "public"."sys_user_role" USING btree (
  "user_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table sys_user_role
-- ----------------------------
ALTER TABLE "public"."sys_user_role" ADD CONSTRAINT "uk_user_role" UNIQUE ("user_id", "role_id");

-- ----------------------------
-- Primary Key structure for table sys_user_role
-- ----------------------------
ALTER TABLE "public"."sys_user_role" ADD CONSTRAINT "sys_user_role_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table sys_role_menu
-- ----------------------------
ALTER TABLE "public"."sys_role_menu" ADD CONSTRAINT "sys_role_menu_menu_id_fkey" FOREIGN KEY ("menu_id") REFERENCES "public"."sys_menu" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."sys_role_menu" ADD CONSTRAINT "sys_role_permission_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_role" ("role_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_user_role
-- ----------------------------
ALTER TABLE "public"."sys_user_role" ADD CONSTRAINT "fk_user_role_role" FOREIGN KEY ("role_id") REFERENCES "public"."sys_role" ("role_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sys_user_role" ADD CONSTRAINT "fk_user_role_user" FOREIGN KEY ("user_id") REFERENCES "public"."sys_user" ("user_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
