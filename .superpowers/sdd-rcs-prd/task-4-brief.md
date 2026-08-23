## Task 4: A* 路径规划

**Files:**
- Create: `rcs/rcs/topology/pathfinder.py`
- Modify: `rcs/rcs/topology/__init__.py`
- Test: `rcs/tests/unit/test_topology_pathfinder.py`

**Interfaces:**
- Consumes: `SiteMap`（来自 Task 3）
- Produces:
  - `find_path(site_map, start_id, goal_id) -> list[str] | None`：返回节点 ID 序列

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_topology_pathfinder.py
from rcs.topology.site_map import SiteMap, SiteNode, SiteEdge, NodeType
from rcs.topology.pathfinder import find_path


def _build_grid():
    sm = SiteMap()
    sm.add_node(SiteNode("A", (0.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("B", (1.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("C", (2.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("D", (1.0, 1.0, 0.0), NodeType.STAGING))
    sm.add_edge(SiteEdge("A", "B", 1.0))
    sm.add_edge(SiteEdge("B", "C", 1.0))
    sm.add_edge(SiteEdge("A", "D", 1.5))
    sm.add_edge(SiteEdge("D", "C", 1.5))
    return sm


def test_find_path_direct():
    sm = _build_grid()
    path = find_path(sm, "A", "B")
    assert path == ["A", "B"]


def test_find_path_indirect():
    sm = _build_grid()
    path = find_path(sm, "A", "C")
    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "C"
    assert len(path) == 3  # A->B->C


def test_find_path_no_route():
    sm = SiteMap()
    sm.add_node(SiteNode("X", (0.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("Y", (5.0, 5.0, 0.0), NodeType.STAGING))
    assert find_path(sm, "X", "Y") is None
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_topology_pathfinder.py -v
```

预期：FAIL（`ModuleNotFoundError`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/topology/pathfinder.py
from __future__ import annotations
import heapq
from .site_map import SiteMap


def _heuristic(sm: SiteMap, a: str, b: str) -> float:
    pa = sm.get_node(a).position
    pb = sm.get_node(b).position
    return ((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2) ** 0.5


def find_path(site_map: SiteMap, start_id: str, goal_id: str) -> list[str] | None:
    if start_id not in site_map.all_nodes() and start_id not in {n.node_id for n in site_map.all_nodes()}:
        return None
    if goal_id not in {n.node_id for n in site_map.all_nodes()}:
        return None
    open_heap: list[tuple[float, str]] = [(0.0, start_id)]
    came_from: dict[str, str] = {}
    g_score: dict[str, float] = {start_id: 0.0}
    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal_id:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return list(reversed(path))
        for edge in site_map.get_neighbors(current):
            tentative = g_score[current] + edge.distance
            if tentative < g_score.get(edge.to_node, float("inf")):
                came_from[edge.to_node] = current
                g_score[edge.to_node] = tentative
                f_score = tentative + _heuristic(site_map, edge.to_node, goal_id)
                heapq.heappush(open_heap, (f_score, edge.to_node))
    return None
```

修改 `rcs/rcs/topology/__init__.py`：

```python
from .site_map import SiteMap, SiteNode, SiteEdge, NodeType
from .pathfinder import find_path

__all__ = ["SiteMap", "SiteNode", "SiteEdge", "NodeType", "find_path"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_topology_pathfinder.py -v
```

预期：PASS（3 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/topology/ rcs/tests/unit/test_topology_pathfinder.py
git commit -m "feat(rcs): add A* pathfinder for site map"
```

---

