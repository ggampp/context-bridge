from __future__ import annotations

from context_bridge.graph.models import KnowledgeGraph
from context_bridge.sync.state import SyncState, compute_graph_hash


def graph_unchanged(graph: KnowledgeGraph, state: SyncState) -> bool:
    """True when the graph fingerprint matches the last recorded sync."""
    if not state.graph_hash:
        return False
    return compute_graph_hash(graph) == state.graph_hash
