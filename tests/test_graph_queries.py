from __future__ import annotations

from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.queries import find_node, hub_nodes, nodes_by_domain, nodes_by_layer, nodes_by_path
from context_bridge.graph.validate import validate_graph


def test_nodes_by_layer(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    layers = nodes_by_layer(graph)
    assert layers["api"]
    assert layers["service"]
    assert len(layers["api"]) == 4


def test_hub_nodes(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    hubs = hub_nodes(graph, min_degree=3, limit=5)
    assert hubs
    assert hubs[0].degree >= 3
    top_ids = {h.node.id for h in hubs}
    assert "node-router" in top_ids


def test_nodes_by_path_exact(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    matches = nodes_by_path(graph, "src/auth/login.ts")
    assert len(matches) >= 1
    assert any(n.type == "file" for n in matches)


def test_find_node_by_path(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    node = find_node(graph, "src/auth/login.ts")
    assert node is not None
    assert node.id == "node-login"


def test_find_node_by_id(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    node = find_node(graph, "node-service")
    assert node is not None
    assert node.layer == "service"


def test_nodes_by_domain(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    domains = nodes_by_domain(graph)
    assert "auth" in domains
    assert len(domains["auth"]) >= 2


def test_validate_graph_ok(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    result = validate_graph(graph)
    assert result.ok
    assert not result.errors
