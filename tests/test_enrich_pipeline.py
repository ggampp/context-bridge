from __future__ import annotations

from context_bridge.enrich.format_json import format_json_dict
from context_bridge.enrich.format_md import format_markdown
from context_bridge.enrich.pipeline import run_enrich
from context_bridge.graph.loader import load_knowledge_graph


class FakeSearchClient:
    def __init__(self, results: list[dict]) -> None:
        self.backend = "fake"
        self._results = results

    def search(self, query, project=None, limit=10):
        return self._results[:limit]


def test_enrich_resolves_node_anchor(sample_project_root):
    client = FakeSearchClient(
        [
            {
                "id": 1,
                "title": "Entry point: router.ts",
                "type": "codebase-map",
                "topic_key": "cb-hub-node-router",
                "content": (
                    "**What**: central node\n"
                    "**Why**: sync\n"
                    "**Where**: .understand-anything/knowledge-graph.json#node:node-router (src/api/router.ts)"
                ),
            }
        ]
    )
    result = run_enrich(sample_project_root, "router", client=client)
    assert result.graph_available
    assert len(result.memories) == 1
    em = result.memories[0]
    assert em.graph_context.anchor_nodes
    assert em.graph_context.anchor_nodes[0].id == "node-router"
    assert em.graph_context.related_nodes  # router has neighbors in fixture


def test_enrich_resolves_layer_anchor(sample_project_root):
    client = FakeSearchClient(
        [
            {
                "id": 2,
                "title": "Architecture layer: api",
                "type": "architecture",
                "topic_key": "cb-layer-api",
                "content": (
                    "**What**: 4 nodes\n"
                    "**Why**: sync\n"
                    "**Where**: .understand-anything/knowledge-graph.json#layer:api"
                ),
            }
        ]
    )
    result = run_enrich(sample_project_root, "api", client=client)
    assert result.memories[0].graph_context.anchor_nodes
    assert all(n.layer == "api" for n in result.memories[0].graph_context.anchor_nodes)


def test_enrich_memory_without_where_still_shown(sample_project_root):
    client = FakeSearchClient(
        [{"id": 3, "title": "Manual note", "type": "decision", "topic_key": "cb-x", "content": "**What**: x"}]
    )
    result = run_enrich(sample_project_root, "note", client=client)
    assert len(result.memories) == 1
    assert result.memories[0].graph_context.is_empty
    assert result.memories[0].graph_context.note


def test_enrich_degrades_gracefully_without_graph(tmp_path):
    client = FakeSearchClient(
        [{"id": 4, "title": "x", "type": "decision", "topic_key": "cb-x", "content": "**What**: x\n**Where**: a.ts"}]
    )
    result = run_enrich(tmp_path, "x", client=client)
    assert not result.graph_available
    assert result.memories[0].graph_context.note == "no knowledge graph available"


def test_enrich_no_results():
    pass  # covered indirectly; explicit empty-result test below


def test_format_markdown_includes_query_and_table(sample_project_root):
    client = FakeSearchClient(
        [
            {
                "id": 1,
                "title": "Entry point: router.ts",
                "type": "codebase-map",
                "topic_key": "cb-hub-node-router",
                "content": (
                    "**What**: central\n**Why**: sync\n"
                    "**Where**: .understand-anything/knowledge-graph.json#node:node-router (src/api/router.ts)"
                ),
            }
        ]
    )
    result = run_enrich(sample_project_root, "router", client=client)
    md = format_markdown(result)
    assert 'Enrich: "router"' in md
    assert "Entry point: router.ts" in md
    assert "Contexto do grafo" in md


def test_format_json_dict_schema_version(sample_project_root):
    client = FakeSearchClient([])
    result = run_enrich(sample_project_root, "nothing", client=client)
    data = format_json_dict(result)
    assert data["version"] == 1
    assert data["query"] == "nothing"
    assert data["memories"] == []
    assert data["graph_nodes"] == []
