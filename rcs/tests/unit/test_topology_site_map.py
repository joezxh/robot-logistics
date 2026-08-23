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
