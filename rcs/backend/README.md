# rcs/backend

RCS 统一后端扩展层。提供：

- 站点拓扑 CRUD（floor_shell / site_grid）
- DXF 导入 / 导出（导出需 ezdxf 可选依赖）
- 6 场景物流模板（电商 / 制造 / 冷链 / 港口 / 退货 / 多层）
- 订单 CRUD

## 运行

```bash
# 开发
cd rcs/backend
pip install -e ".[dev]"
pytest -v
uvicorn rcs_backend.main:app --reload --port 8100

# Docker
docker build -f rcs/backend/Dockerfile -t rcs-backend .
docker run -p 8100:8100 rcs-backend
```

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `RCS_API_KEY` | `` | API 密钥（留空则禁用） |
| `RCS_STORAGE` | `memory` | 存储后端（`memory` / `sqlite` / `postgres`） |
| `RCS_DB_PATH` | `/tmp/rcs.db` | SQLite 路径 |
| `RCS_DATABASE_URL` | `postgresql+asyncpg://rcs:rcs@localhost:5432/rcs` | PostgreSQL 连接（storage=postgres 时生效） |

## REST API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/rcs/topology/shell` | 列出所有 shell |
| GET | `/api/rcs/topology/shell/{site_id}` | 获取 shell |
| PUT | `/api/rcs/topology/shell/{site_id}` | 保存 shell（自动校验） |
| GET | `/api/rcs/topology/grid/{site_id}` | 获取 grid |
| PUT | `/api/rcs/topology/grid/{site_id}` | 保存 grid |
| POST | `/api/rcs/topology/import/dxf` | 解析上传的 DXF |
| POST | `/api/rcs/topology/import/dxf/{site_id}` | 上传 + 保存 |
| POST | `/api/rcs/topology/export/dxf` | 导出 DXF（需 ezdxf） |
| POST | `/api/rcs/topology/export/dxf/{site_id}` | 导出已存 shell |
| GET | `/api/rcs/topology/templates` | 列出 6 场景模板 |
| GET | `/api/rcs/topology/templates/{scenario_id}` | 获取单个模板 |
| POST | `/api/rcs/orders` | 创建订单（202） |
| GET | `/api/rcs/orders/{order_id}` | 获取订单状态 |

## 6 场景 ID

`ecommerce`, `manufacturing`, `cold_chain`, `port`, `reverse_logistics`, `multi_floor`
