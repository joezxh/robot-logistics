## Task 3: 站点地图数据结构

**Files:**
- Create: `rcs/rcs/topology/site_map.py`
- Create: `rcs/rcs/topology/__init__.py`
- Test: `rcs/tests/unit/test_topology_site_map.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `SiteNode` dataclass（node_id, position, type, capacity）
  - `SiteEdge` dataclass（from_node, to_node, distance, speed_limit）
  - `SiteMap` class：`add_node()`, `add_edge()`, `get_neighbors()`, `get_node()`

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_topology_site_map.py
from rcs.topology.site_map import SiteMap, SiteNode, SiteEdge, NodeType


def test_site_map_add_and_get_node():
    sm = SiteMap()
    node = SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK, capacity=10)
    sm.add_node(node)
    assert sm.get_node("A1") == node


def test_site_map_add_edge_and_neighbors():
    sm = SiteMap()
    sm.add_node(SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK))
    sm.add_node(SiteNode(node_id="A2", position=(1.0, 0.0, 0.0), type=NodeType.PICK))
    sm.add_edge(SiteEdge(from_node="A1", to_node="A2", distance=1.0, speed_limit=1.5))
    neighbors = sm.get_neighbors("A1")
    assert len(neighbors) == 1
    assert neighbors[0].to_node == "A2"


def test_site_map_duplicate_node_raises():
    sm = SiteMap()
    sm.add_node(SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK))
    try:
        sm.add_node(SiteNode(node_id="A1", position=(1.0, 0.0, 0.0), type=NodeType.PLACE))
        assert False, "should have raised"
    except ValueError:
        pass
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_topology_site_map.py -v
```

预期：FAIL（`ModuleNotFoundError`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/topology/site_map.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class NodeType(str, Enum):
    PICK = "pick"
    PLACE = "place"
    STAGING = "staging"
    CHARGING = "charging"
    LOADING = "loading"
    UNLOADING = "unloading"


@dataclass
class SiteNode:
    node_id: str
    position: tuple[float, float, float]
    type: NodeType
    capacity: int = 1
    metadata: dict = field(default_factory=dict)


@dataclass
class SiteEdge:
    from_node: str
    to_node: str
    distance: float
    speed_limit: float = 1.0
    bidirectional: bool = True


class SiteMap:
    def __init__(self) -> None:
        self._nodes: dict[str, SiteNode] = {}
        self._adjacency: dict[str, list[SiteEdge]] = {}

    def add_node(self, node: SiteNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node_id: {node.node_id}")
        self._nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, [])

    def get_node(self, node_id: str) -> SiteNode:
        if node_id not in self._nodes:
            raise KeyError(f"unknown node_id: {node_id}")
        return self._nodes[node_id]

    def add_edge(self, edge: SiteEdge) -> None:
        if edge.from_node not in self._nodes:
            raise KeyError(f"unknown node_id: {edge.from_node}")
        if edge.to_node not in self._nodes:
            raise KeyError(f"unknown node_id: {edge.to_node}")
        self._adjacency[edge.from_node].append(edge)
        if edge.bidirectional:
            self._adjacency[edge.to_node].append(
                SiteEdge(edge.to_node, edge.from_node, edge.distance, edge.speed_limit, False)
            )

    def get_neighbors(self, node_id: str) -> list[SiteEdge]:
        if node_id not in self._adjacency:
            raise KeyError(f"unknown node_id: {node_id}")
        return self._adjacency[node_id]

    def all_nodes(self) -> list[SiteNode]:
        return list(self._nodes.values())
```

```python
# rcs/rcs/topology/__init__.py
from .site_map import SiteMap, SiteNode, SiteEdge, NodeType

__all__ = ["SiteMap", "SiteNode", "SiteEdge", "NodeType"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_topology_site_map.py -v
```

预期：PASS（3 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/topology/ rcs/tests/unit/test_topology_site_map.py
git commit -m "feat(rcs): add site map with node/edge structures"
```

---

