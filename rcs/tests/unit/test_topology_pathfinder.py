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