# RCS Frontend (v2)

现代化仓库可视化前端，对标 RCS（Robot Control Stack）拓扑蓝图。
基于 **Vite + Vue 3 + TypeScript + Pinia + vue-i18n + ECharts + Three.js** 构建。

## 功能

- **6 种业务场景**的一键切换：电商仓、生产制造、冷链仓、港口码头、逆向物流、多层仓
- **二维平面图**（ECharts custom series）：按 `FloorShell` 的真实 X/Z 尺寸绘制区域矩形
- **三维场景**（Three.js `ShellScene` + OrbitControls）：地面、区域体块、墙体，支持楼层切换
- **场景化指标面板**：按场景高亮相关区域类型，展示区域分布与告警类型
- **中/英双语**（`zh-CN` / `en-US`），运行时切换

## 目录结构

```
src/
├── api/                 # REST 客户端（http + topologyShell/templates/orders）
├── components/
│   ├── DeviceMap2D/     # ECharts 二维地图（option.ts 为纯函数，便于测试）
│   ├── DeviceMap3D/     # Three.js 三维场景（ShellScene.ts 为纯几何构建）
│   └── scenarios/       # 场景配置 + ScenarioPanel
├── i18n/                # 双语文案与辅助函数
├── stores/              # Pinia：scenario / floorShell / siteGrid
├── types/               # 与后端 Pydantic 模型对齐的 TS 类型
├── views/SiteMapView.vue# 主视图：场景选择 + 2D/3D 切换 + 楼层选择
└── styles/tokens.css    # 设计令牌（暗色主题）
```

## 开发

```bash
corepack enable            # 启用 pnpm
pnpm install
pnpm dev                   # http://localhost:5173
pnpm test                  # 运行 vitest 单元测试
pnpm run build             # vue-tsc 类型检查 + vite 生产构建
```

前端通过 Vite 代理把 `/api/rcs` 转发到 RCS 后端（`http://localhost:8100`）。
生产环境由 nginx 反向代理（见 `nginx.conf`）。

## 与后端 API 的对应

| 前端调用 | 后端路由 |
|----------|----------|
| `listShells()` | `GET /api/rcs/topology/shell` |
| `getShell(id)` | `GET /api/rcs/topology/shell/{id}` |
| `listTemplates()` | `GET /api/rcs/topology/templates` |
| `getTemplate(id)` | `GET /api/rcs/topology/templates/{id}` |
| `createOrder(req)` | `POST /api/rcs/orders` |
| `getOrder(id)` | `GET /api/rcs/orders/{id}` |

## 容器化

```bash
docker compose up --build
# 前端 http://localhost:8080 ，后端 http://localhost:8100
```

多阶段 `Dockerfile`：先 `pnpm build` 产出静态文件，再由 nginx 托管；
`docker-compose.yml` 同时编排前端与 RCS 后端（请按需替换 `rcs-backend` 镜像）。

## 测试

全部 62 个单元测试覆盖类型、API 客户端、Pinia store、i18n、2D/3D 地图、场景组件与主视图，
均通过 TDD（先写测试 → 失败 → 实现 → 通过）方式完成。
