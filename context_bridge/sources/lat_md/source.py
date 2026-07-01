from __future__ import annotations

from pathlib import Path

from context_bridge.graph.loader import load_graph_json_file
from context_bridge.graph.models import KnowledgeGraph
from context_bridge.sources.lat_md.builder import build_lat_graph, compute_lat_source_hash, lat_graph_path, write_lat_graph


class LatMdSource:
    name = "lat-md"

    def available(self, project_root: Path) -> bool:
        root = Path(project_root)
        return lat_graph_path(root).is_file() or (root / "lat.md").is_dir()

    def load(self, project_root: Path, *, use_cache: bool = True) -> KnowledgeGraph:
        root = Path(project_root)
        graph_path = lat_graph_path(root)
        lat_dir = root / "lat.md"

        if graph_path.is_file() and not lat_dir.is_dir():
            # No lat.md/ tree to rebuild from (e.g. a distributed snapshot) —
            # read the prebuilt file as-is.
            return load_graph_json_file(graph_path)

        current_hash = compute_lat_source_hash(root)
        if graph_path.is_file():
            cached = load_graph_json_file(graph_path)
            if cached.metadata.get("source_hash") == current_hash:
                return cached

        graph = build_lat_graph(root)
        write_lat_graph(root, graph, graph_path)
        return graph
