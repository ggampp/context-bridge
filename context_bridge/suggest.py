from __future__ import annotations

from pathlib import Path

from context_bridge.core.paths import resolve_project_paths
from context_bridge.engram.payloads import MemSavePayload
from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.sync.engine import collect_payloads
from context_bridge.sync.rules import SyncRules, load_sync_rules


def build_suggestions(
    project: str | Path | None = None,
    *,
    types: set[str] | None = None,
    rules: SyncRules | None = None,
) -> list[MemSavePayload]:
    """Generate mem_save payloads from the graph without touching Engram.

    Reuses the same mappers as `sync` (Sprint 3) — this is a read-only,
    side-effect-free preview, useful for agents deciding what to persist.
    """
    paths = resolve_project_paths(project)
    graph = load_knowledge_graph(paths.project_root)
    rules = rules or load_sync_rules()
    return collect_payloads(graph, rules, project=paths.project_root.name, types=types)
