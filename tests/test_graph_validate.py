from __future__ import annotations

import json

from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.validate import validate_graph


def test_validate_empty_nodes_fails():
    from context_bridge.graph.models import KnowledgeGraph

    graph = KnowledgeGraph(version="", nodes=[], edges=[])
    result = validate_graph(graph)
    assert not result.ok
    assert any("no nodes" in e.message.lower() for e in result.errors)


def test_validate_dangling_edge_warning(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    graph.edges.append(
        type(graph.edges[0])(
            source="missing-node",
            target="node-login",
            type="calls",
        )
    )
    result = validate_graph(graph)
    assert result.ok
    assert any("missing-node" in w.message for w in result.warnings)


def test_validate_duplicate_ids():
    from context_bridge.graph.models import GraphNode, KnowledgeGraph

    graph = KnowledgeGraph(
        version="1",
        nodes=[
            GraphNode(id="dup", label="a"),
            GraphNode(id="dup", label="b"),
        ],
        edges=[],
    )
    result = validate_graph(graph)
    assert not result.ok
    assert any("duplicate" in e.message.lower() for e in result.errors)


def test_validate_missing_version_warns(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    graph.version = ""
    result = validate_graph(graph)
    assert result.ok
    assert any("version" in w.message.lower() for w in result.warnings)
