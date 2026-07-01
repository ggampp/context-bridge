from __future__ import annotations

from dataclasses import dataclass, field

from context_bridge.enrich.where_parser import ParsedWhere
from context_bridge.graph.models import GraphNode, KnowledgeGraph
from context_bridge.graph.queries import neighbors, nodes_by_domain, nodes_by_layer, nodes_by_path


@dataclass(frozen=True)
class GraphContextResult:
    anchor_nodes: list[GraphNode] = field(default_factory=list)
    related_nodes: list[GraphNode] = field(default_factory=list)
    note: str = ""

    @property
    def all_nodes(self) -> list[GraphNode]:
        seen: set[str] = set()
        ordered: list[GraphNode] = []
        for node in [*self.anchor_nodes, *self.related_nodes]:
            if node.id not in seen:
                seen.add(node.id)
                ordered.append(node)
        return ordered

    @property
    def is_empty(self) -> bool:
        return not self.anchor_nodes and not self.related_nodes


def _anchor_nodes_for(parsed: ParsedWhere, graph: KnowledgeGraph) -> list[GraphNode]:
    if parsed.kind == "node":
        node = graph.node_by_id(parsed.value)
        return [node] if node else []

    if parsed.kind == "layer":
        return nodes_by_layer(graph).get(parsed.value, [])

    if parsed.kind == "domain":
        return nodes_by_domain(graph).get(parsed.value, [])

    if parsed.kind == "path":
        found: list[GraphNode] = []
        for path in parsed.paths:
            found.extend(nodes_by_path(graph, path))
        return found

    return []


def resolve_graph_context(
    parsed: ParsedWhere,
    graph: KnowledgeGraph | None,
    *,
    hops: int = 1,
    limit: int = 15,
) -> GraphContextResult:
    """Resolve a parsed `where` hint into anchor nodes + their neighbors.

    Degrades gracefully: returns an empty, annotated result when there is no
    graph available or the hint doesn't resolve to anything — callers should
    still show the memory itself.
    """
    if graph is None:
        return GraphContextResult(note="no knowledge graph available")

    if parsed.is_empty:
        return GraphContextResult(note="memory has no resolvable 'where' field")

    anchors = _anchor_nodes_for(parsed, graph)[:limit]
    if not anchors:
        return GraphContextResult(note=f"no graph nodes matched '{parsed.value or parsed.paths}'")

    related: list[GraphNode] = []
    seen = {n.id for n in anchors}
    for anchor in anchors:
        for n in neighbors(graph, anchor.id, hops=hops, limit=limit):
            if n.id not in seen and len(related) < limit:
                seen.add(n.id)
                related.append(n)

    return GraphContextResult(anchor_nodes=anchors, related_nodes=related)
