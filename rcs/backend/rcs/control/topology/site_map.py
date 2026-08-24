"""SiteMap: nodes and edges describing a robot facility floor."""
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
