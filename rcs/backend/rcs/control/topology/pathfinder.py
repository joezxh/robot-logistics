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