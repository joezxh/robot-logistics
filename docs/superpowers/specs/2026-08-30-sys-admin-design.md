# RCS 系统管理模块 + 控制台重构 设计文档

**日期**：2026-08-30
**范围**：`rcs/backend`（FastAPI + 异步 SQLAlchemy）、`rcs/frontend`（Vue 3 + TS + Ant Design Vue）
**数据库**：PostgreSQL，表定义以 `rcs/docs/sys.sql` 为准

---

## 1. 目标与决策

| 决策项 | 结论 |
|---|---|
| 菜单多语言存储 | `sys_menu` 新增 `i18n JSONB` 单列，形如 `{"zh-CN":"设备管理","en-US":"Devices","zh-TW":"設備管理","ja-JP":"デバイス管理"}`，`name` 列作为回退值 |
| 现有页面归属 | 全部纳入权限菜单（作为菜单种子写入 `sys_menu`）；顶栏保留「门户」入口直达站点地图 / 仓库视图 / 设备控制三个大屏页 |
| 鉴权范围 | 复用 `Settings.auth_enabled` 开关（默认 `False`）。`/api/sys/**` 始终强制 JWT；`/api/rcs/**` 仅在 `auth_enabled=True` 时校验 |
| 前端 UI 库 | 引入 Ant Design Vue v4，与 `risk_control` 前端保持一致 |

---

## 2. 后端架构

新增包 `rcs/sysadmin/`，与既有 `rcs/api/`、`rcs/control/` 平级，不改动既有业务代码。

```
rcs/sysadmin/
├── models.py      # 8 张 sys_* 表 ORM（Mapped/mapped_column 风格，与 rcs/db/models.py 一致）
├── schemas.py     # Pydantic v2 请求/响应模型
├── security.py    # bcrypt 哈希 + PyJWT 签发/校验
├── deps.py        # 异步会话、当前用户、管理员/权限校验依赖
├── audit.py       # 审计日志异步批量写入 + AuditRoute 路由类
├── service.py     # 业务逻辑（用户/角色/菜单/字典 CRUD、菜单树、权限解析）
├── seed.py        # 初始化种子数据
└── routers/
    ├── auth.py    # /api/sys/auth/*
    ├── users.py   # /api/sys/users*
    ├── roles.py   # /api/sys/roles*
    ├── menus.py   # /api/sys/menus*
    ├── audit.py   # /api/sys/audit-logs
    └── dicts.py   # /api/sys/dictionaries*
```

### 2.1 数据模型要点

- 沿用 `rcs.db.models.Base`，`init_db()` 的 `create_all` 自动纳管；列定义逐一对齐 `sys.sql` 的 `timestamp(6)`（naive `DateTime`）语义。
- 关联关系统一 `lazy="selectin"`，避免 asyncpg 下 `MissingGreenlet`。
- `sys_menu` 扩展列：`i18n JSONB`（迁移脚本 `migrations/003_sys_admin.sql` 负责 `ADD COLUMN IF NOT EXISTS`）。

### 2.2 认证与授权

- 登录 `POST /api/sys/auth/login` → 校验 bcrypt → 签发 JWT（`sub` = user_id，HS256，可配置有效期）。
- `deps.get_current_user` 解析 Bearer Token → 查库 → 校验 `status == active`。
- `is_admin=True` 或角色码含 `super_admin` 的用户直接获得通配权限 `*:*`。
- 权限标识取自 `sys_menu.permission`，经 `sys_role_menu` → `sys_user_role` 汇总。
- 审计：`AuditRoute(APIRoute)` 子类在路由处理前后采集 method/url/耗时/状态码/请求体（敏感字段脱敏），投递到内存队列，由后台协程批量落库，不阻塞请求。

### 2.3 响应约定

沿用参考实现风格：列表/写操作返回 `{"code": 0, "message": "success", "data": ..., "total": N}`；登录与 `/me` 返回裸对象。

---

## 3. 前端架构

### 3.1 目录

```
src/
├── api/sys*.ts        # sysHttp（自动注入 Bearer + 401 跳登录）+ 各模块 API
├── types/sys.ts       # 用户/角色/菜单/审计/字典类型
├── stores/auth.ts     # token、用户信息、权限、动态菜单
├── stores/app.ts      # 主题（dark/light）、语言、侧栏折叠
├── stores/dict.ts     # 字典缓存
├── i18n/              # zh-CN / zh-TW / en-US / ja-JP
├── styles/tokens.css  # 深/浅两套 CSS 变量（科技感）
├── layouts/ConsoleLayout.vue + components/{AppSidebar,AppHeader,UserDropdown}.vue
├── router/index.ts    # 静态路由（login/404）+ 登录后按菜单动态 addRoute
└── views/
    ├── LoginView.vue / DashboardView.vue / ProfileView.vue
    └── system/{UserManage,RoleManage,MenuManage,AuditLog,DictManage}.vue
```

### 3.2 动态菜单与路由

1. 登录后调用 `/api/sys/auth/me/menus` 取回菜单树（含 `i18n` 多语言字段）。
2. `buildRoutes(tree)` 按 `component` 字段映射到 `views/` 下的组件（`import.meta.glob` 懒加载），以 `addRoute('console', ...)` 注入。
3. 侧栏渲染同一棵树；菜单标题按当前语言取 `i18n[locale] ?? name`。
4. 路由守卫：无 token → `/login`；未加载菜单 → 先加载；`permission` 缺失则拒绝进入。

### 3.3 主题与多语言

- `data-theme="dark|light"` 挂在 `<html>`，全部颜色走 CSS 变量；AntD 通过 `ConfigProvider` 的 `theme.algorithm`（`darkAlgorithm` / `defaultAlgorithm`）同步切换。
- 语言切换持久化到 `localStorage`，并同步 AntD `locale`（`zh_CN` / `zh_TW` / `en_US` / `ja_JP`）。

---

## 4. 初始化数据

`scripts/init_sys_data.py`（亦可 `python -m rcs.sysadmin.seed`）：

- 角色：`super_admin`（超管）、`admin`（系统管理员）、`operator`（调度操作员）、`viewer`（只读访客）
- 用户：`admin / admin123`（超管，`is_admin=true`）、`operator / operator123`、`viewer / viewer123`
- 菜单：控制台、设备、地图、订单、调度、日志、站点地图、仓库视图、设备控制、系统管理（用户/角色/菜单/审计/字典），每项含四语言 `i18n`
- 字典：`user_status`、`menu_type`、`operation_type`、`robot_morphology`、`order_status`、`log_level`

---

## 5. 风险与权衡

- **既有前端测试**：`src/**/*.spec.ts` 会在 jsdom 下运行，新增 AntD 依赖后需保证这些测试不挂载依赖 AntD 的组件；`i18n` 重构保留 `messages` 导出与 `scenarios`/`zone` 结构。
- **既有后端测试**：`auth_enabled` 默认 `False`，`/api/rcs/**` 行为不变，现有集成测试不受影响。
- **审计写入**：队列满时降级为丢弃并告警，绝不阻塞业务请求。
