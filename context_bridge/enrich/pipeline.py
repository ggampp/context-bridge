from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from context_bridge.core.paths import resolve_project_paths
from context_bridge.engram.client import EngramClient
from context_bridge.enrich.graph_context import GraphContextResult, resolve_graph_context
from context_bridge.enrich.where_parser import extract_where_line, parse_where
from context_bridge.graph.models import GraphNode, KnowledgeGraph
from context_bridge.sources.resolver import resolve_graph

ENRICH_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class EnrichedMemory:
    memory: dict[str, Any]
    graph_context: GraphContextResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.memory.get("id"),
            "title": self.memory.get("title"),
            "type": self.memory.get("type"),
            "topic_key": self.memory.get("topic_key"),
            "content": self.memory.get("content"),
            "graph_nodes": [_node_dict(n) for n in self.graph_context.all_nodes],
            "graph_note": self.graph_context.note or None,
        }


@dataclass(frozen=True)
class EnrichResult:
    query: str
    memories: list[EnrichedMemory] = field(default_factory=list)
    graph_available: bool = False
    version: int = ENRICH_SCHEMA_VERSION

    @property
    def graph_nodes(self) -> list[GraphNode]:
        seen: set[str] = set()
        ordered: list[GraphNode] = []
        for em in self.memories:
            for node in em.graph_context.all_nodes:
                if node.id not in seen:
                    seen.add(node.id)
                    ordered.append(node)
        return ordered

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "query": self.query,
            "graph_available": self.graph_available,
            "memories": [m.to_dict() for m in self.memories],
            "graph_nodes": [_node_dict(n) for n in self.graph_nodes],
        }


def _node_dict(node: GraphNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "label": node.label,
        "path": node.path,
        "layer": node.layer,
        "summary": node.summary,
    }


def _load_graph_safely(project: str | Path | None) -> KnowledgeGraph | None:
    try:
        return resolve_graph(project)
    except (FileNotFoundError, ValueError):
        return None


def run_enrich(
    project: str | Path | None = None,
    query: str = "",
    *,
    limit: int = 10,
    hops: int = 1,
    node_limit: int = 15,
    client: EngramClient | None = None,
) -> EnrichResult:
    paths = resolve_project_paths(project)
    graph = _load_graph_safely(paths.project_root)

    client = client or EngramClient()
    raw_memories = client.search(query, project=paths.project_root.name, limit=limit)

    enriched: list[EnrichedMemory] = []
    for memory in raw_memories:
        if not isinstance(memory, dict):
            continue
        where_text = memory.get("where") or extract_where_line(memory.get("content", "")) or ""
        parsed = parse_where(where_text)
        context = resolve_graph_context(parsed, graph, hops=hops, limit=node_limit)
        enriched.append(EnrichedMemory(memory=memory, graph_context=context))

    return EnrichResult(query=query, memories=enriched, graph_available=graph is not None)
