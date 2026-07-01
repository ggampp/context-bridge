from __future__ import annotations

import json
import logging
from pathlib import Path

from context_bridge.core.paths import ProjectPaths, resolve_project_paths
from context_bridge.graph.models import GraphConfig, GraphEdge, GraphNode, KnowledgeGraph

logger = logging.getLogger(__name__)

# Supported top-level fields in knowledge-graph.json (UA may extend over time).
_GRAPH_TOP_LEVEL = {"version", "nodes", "edges", "metadata", "domains", "tours", "languages"}
_NODE_FIELDS = {"id", "label", "type", "path", "layer", "summary", "domain", "language"}
_EDGE_FIELDS = {"source", "target", "type", "from", "to"}

_CACHE: dict[str, KnowledgeGraph] = {}


def clear_graph_cache() -> None:
    _CACHE.clear()


def _load_json(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise FileNotFoundError(f"Cannot read {path}: {e}") from e
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}, got {type(data).__name__}")
    return data


def _warn_unknown_fields(data: dict, known: set[str], context: str) -> None:
    unknown = set(data.keys()) - known
    for key in sorted(unknown):
        logger.warning("Unknown %s field ignored: %s", context, key)


def _parse_nodes(raw_nodes: object) -> list[GraphNode]:
    if not isinstance(raw_nodes, list):
        raise ValueError("'nodes' must be a JSON array")
    nodes: list[GraphNode] = []
    for i, item in enumerate(raw_nodes):
        if not isinstance(item, dict):
            raise ValueError(f"nodes[{i}] must be an object")
        if not item.get("id"):
            raise ValueError(f"nodes[{i}] missing required field 'id'")
        _warn_unknown_fields(item, _NODE_FIELDS, f"nodes[{i}]")
        nodes.append(GraphNode.from_dict(item))
    return nodes


def _parse_edges(raw_edges: object) -> list[GraphEdge]:
    if raw_edges is None:
        return []
    if not isinstance(raw_edges, list):
        raise ValueError("'edges' must be a JSON array")
    edges: list[GraphEdge] = []
    for i, item in enumerate(raw_edges):
        if not isinstance(item, dict):
            raise ValueError(f"edges[{i}] must be an object")
        edge = GraphEdge.from_dict(item)
        if not edge.source or not edge.target:
            raise ValueError(f"edges[{i}] missing source/target")
        _warn_unknown_fields(item, _EDGE_FIELDS, f"edges[{i}]")
        edges.append(edge)
    return edges


def load_graph_json_file(path: Path) -> KnowledgeGraph:
    """Parse a standalone UA-schema graph JSON file (e.g. `.context-bridge/lat-graph.json`).

    Shares the same parsing/validation rules as `load_knowledge_graph`, but
    reads an arbitrary path instead of resolving `.understand-anything/`.
    Used by non-UA GraphSource implementations (see `context_bridge/sources/`).
    """
    data = _load_json(path)
    _warn_unknown_fields(data, _GRAPH_TOP_LEVEL, "knowledge-graph root")
    return KnowledgeGraph(
        version=str(data.get("version", "")),
        nodes=_parse_nodes(data.get("nodes", [])),
        edges=_parse_edges(data.get("edges", [])),
        config=GraphConfig(),
        metadata=dict(data.get("metadata") or {}),
        source_path=str(path),
    )


def load_config(paths: ProjectPaths) -> GraphConfig:
    if not paths.ua_config.is_file():
        return GraphConfig()
    data = _load_json(paths.ua_config)
    return GraphConfig.from_dict(data)


def load_knowledge_graph(
    project: str | Path | None = None,
    *,
    use_cache: bool = True,
) -> KnowledgeGraph:
    paths = resolve_project_paths(project)
    cache_key = str(paths.knowledge_graph)
    if use_cache and cache_key in _CACHE:
        return _CACHE[cache_key]

    if not paths.has_knowledge_graph:
        raise FileNotFoundError(
            f"Knowledge graph not found at {paths.knowledge_graph}. "
            "Run /understand in Understand Anything first."
        )

    data = _load_json(paths.knowledge_graph)
    _warn_unknown_fields(data, _GRAPH_TOP_LEVEL, "knowledge-graph root")

    graph = KnowledgeGraph(
        version=str(data.get("version", "")),
        nodes=_parse_nodes(data.get("nodes", [])),
        edges=_parse_edges(data.get("edges", [])),
        config=load_config(paths),
        metadata=dict(data.get("metadata") or {}),
        source_path=str(paths.knowledge_graph),
    )

    if use_cache:
        _CACHE[cache_key] = graph
    return graph
