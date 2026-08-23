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
| `RCS_STORAGE` | `memory` | 存储后端（`memory` / `sqlite`） |
| `RCS_DB_PATH` | `/tmp/rcs.db` | SQLite 路径 |
| `RCS_SERVICE_URL` | `http://127.0.0.1:8101` | rcs/rcs 子项目 URL |
| `RCS_EMBEDDED` | `0` | 是否嵌入式（1=导入 rcs 子项目） |
