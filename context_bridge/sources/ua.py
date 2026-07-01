from __future__ import annotations

from pathlib import Path

from context_bridge.core.paths import resolve_project_paths
from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.models import KnowledgeGraph

# Thin GraphSource adapter over context_bridge.graph.loader — kept separate
# rather than moving the parsing code here, since graph.loader is imported
# directly by many other modules and by most of the test suite (see
# docs/adr/002-sources-layer.md for why this direction was chosen).


class UASource:
    name = "ua"

    def available(self, project_root: Path) -> bool:
        return resolve_project_paths(project_root).has_knowledge_graph

    def load(self, project_root: Path, *, use_cache: bool = True) -> KnowledgeGraph:
        return load_knowledge_graph(project_root, use_cache=use_cache)
