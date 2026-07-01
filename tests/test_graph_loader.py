from __future__ import annotations

import json
from pathlib import Path

import pytest

from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.models import GraphEdge, GraphNode


def test_load_knowledge_graph(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    assert graph.node_count == 5
    assert graph.edge_count == 7
    assert graph.version == "1.0.0-test"
    assert graph.config.language == "en"


def test_load_missing_graph_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="understand"):
        load_knowledge_graph(tmp_path)


def test_load_invalid_json(tmp_path):
    ua = tmp_path / ".understand-anything"
    ua.mkdir()
    (ua / "knowledge-graph.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_knowledge_graph(tmp_path)


def test_load_node_without_id_fails(tmp_path):
    ua = tmp_path / ".understand-anything"
    ua.mkdir()
    (ua / "knowledge-graph.json").write_text(
        json.dumps({"nodes": [{"label": "x"}]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required field 'id'"):
        load_knowledge_graph(tmp_path)


def test_graph_cache(sample_project_root):
    g1 = load_knowledge_graph(sample_project_root)
    g2 = load_knowledge_graph(sample_project_root)
    assert g1 is g2


def test_graph_edge_from_to_aliases():
    edge = GraphEdge.from_dict({"from": "a", "to": "b", "type": "calls"})
    assert edge.source == "a"
    assert edge.target == "b"


def test_graph_node_from_dict():
    node = GraphNode.from_dict({"id": "n1", "path": "src/x.ts", "custom": True})
    assert node.id == "n1"
    assert node.extra.get("custom") is True
