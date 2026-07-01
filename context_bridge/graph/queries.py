from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from context_bridge.graph.models import GraphNode, KnowledgeGraph


@dataclass(frozen=True)
class HubNode:
    node: GraphNode
    degree: int


def _degree_map(graph: KnowledgeGraph) -> dict[str, int]:
    degree: Counter[str] = Counter()
    for edge in graph.edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
    return dict(degree)


def nodes_by_layer(graph: KnowledgeGraph, *, min_nodes: int = 1) -> dict[str, list[GraphNode]]:
    grouped: dict[str, list[GraphNode]] = defaultdict(list)
    for node in graph.nodes:
        layer = node.layer or "unknown"
        grouped[layer].append(node)
    return {layer: nodes for layer, nodes in sorted(grouped.items()) if len(nodes) >= min_nodes}


def hub_nodes(graph: KnowledgeGraph, *, min_degree: int = 5, limit: int = 20) -> list[HubNode]:
    degree = _degree_map(graph)
    hubs: list[HubNode] = []
    for node in graph.nodes:
        d = degree.get(node.id, 0)
        if d >= min_degree:
            hubs.append(HubNode(node=node, degree=d))
    hubs.sort(key=lambda h: (-h.degree, h.node.label or h.node.id))
    return hubs[:limit]


def nodes_by_path(graph: KnowledgeGraph, path: str) -> list[GraphNode]:
    path = path.replace("\\", "/").strip("/")
    exact: list[GraphNode] = []
    prefix: list[GraphNode] = []
    for node in graph.nodes:
        if not node.path:
            continue
        node_path = node.path.replace("\\", "/").strip("/")
        if node_path == path:
            exact.append(node)
        elif node_path.startswith(path + "/") or path.startswith(node_path + "/"):
            prefix.append(node)
    return exact or prefix


def find_node(graph: KnowledgeGraph, identifier: str) -> GraphNode | None:
    identifier = identifier.strip()
    by_id = graph.node_by_id(identifier)
    if by_id:
        return by_id
    matches = nodes_by_path(graph, identifier)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        for node in matches:
            if node.path.replace("\\", "/") == identifier.replace("\\", "/"):
                return node
        return matches[0]
    norm = identifier.replace("\\", "/")
    for node in graph.nodes:
        if node.label == identifier:
            return node
        if node.path and node.path.replace("\\", "/") == norm:
            return node
    return None


def nodes_by_domain(graph: KnowledgeGraph) -> dict[str, list[GraphNode]]:
    grouped: dict[str, list[GraphNode]] = defaultdict(list)
    for node in graph.nodes:
        if node.domain:
            grouped[node.domain].append(node)
    domains_raw = graph.metadata.get("domains")
    if isinstance(domains_raw, dict):
        for domain_name, entries in domains_raw.items():
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, str):
                        node = graph.node_by_id(entry)
                        if node:
                            grouped[domain_name].append(node)
    return dict(sorted(grouped.items()))


def neighbors(graph: KnowledgeGraph, node_id: str, *, hops: int = 1, limit: int = 50) -> list[GraphNode]:
    """BFS over edges (treated as undirected) up to `hops` levels from node_id.

    Excludes the origin node itself. Used by enrich to surface nearby context
    without exploding combinatorially on dense graphs.
    """
    if hops < 1:
        return []

    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph.edges:
        adjacency[edge.source].add(edge.target)
        adjacency[edge.target].add(edge.source)

    visited = {node_id}
    frontier = {node_id}
    for _ in range(hops):
        next_frontier: set[str] = set()
        for current in frontier:
            next_frontier |= adjacency.get(current, set()) - visited
        if not next_frontier:
            break
        visited |= next_frontier
        frontier = next_frontier

    visited.discard(node_id)
    result = [graph.node_by_id(nid) for nid in visited]
    nodes = [n for n in result if n is not None]
    nodes.sort(key=lambda n: n.label or n.id)
    return nodes[:limit]


def graph_languages(graph: KnowledgeGraph) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for node in graph.nodes:
        lang = node.language or graph.config.language
        if lang:
            counts[lang] += 1
    langs_meta = graph.metadata.get("languages")
    if isinstance(langs_meta, dict):
        for lang, count in langs_meta.items():
            counts[str(lang)] += int(count) if isinstance(count, int) else 1
    return dict(counts.most_common())
