from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from context_bridge.core.paths import resolve_project_paths
from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.models import KnowledgeGraph
from context_bridge.sources.base import GraphSource
from context_bridge.sources.lat_md import LatMdSource, lat_graph_path
from context_bridge.sources.ua import UASource

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "graph-source.yaml"
_DEFAULT_PRIORITY: tuple[str, ...] = ("ua", "lat-md")

# UA stays first by default so existing UA-only projects are unaffected —
# lat.md is a complementary source, not a replacement (see docs/SOURCES.md).
_REGISTRY: dict[str, GraphSource] = {"ua": UASource(), "lat-md": LatMdSource()}

# Default `where=` prefix per source, used by sync mappers when
# `sync-rules.yaml` doesn't set an explicit `graph_ref` override.
_GRAPH_REF_BY_SOURCE: dict[str, str] = {
    "ua": ".understand-anything/knowledge-graph.json",
    "lat-md": ".context-bridge/lat-graph.json",
}


def default_graph_ref(source_name: str | None) -> str:
    return _GRAPH_REF_BY_SOURCE.get(source_name or "ua", _GRAPH_REF_BY_SOURCE["ua"])


def graph_file_path(project_root: str | Path, source_name: str | None) -> Path:
    """Path to the on-disk graph file for the given source (for mtime/age checks)."""
    paths = resolve_project_paths(project_root)
    if source_name == "lat-md":
        return lat_graph_path(paths.project_root)
    return paths.knowledge_graph


@dataclass(frozen=True)
class GraphSourceConfig:
    priority: tuple[str, ...] = _DEFAULT_PRIORITY


def load_graph_source_config(path: str | Path | None = None) -> GraphSourceConfig:
    config_path = Path(path) if path else _DEFAULT_CONFIG_PATH
    if not config_path.is_file():
        return GraphSourceConfig()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    priority = data.get("priority")
    if isinstance(priority, list) and priority:
        return GraphSourceConfig(priority=tuple(str(p) for p in priority))
    return GraphSourceConfig()


def resolve_graph(
    project: str | Path | None = None,
    *,
    config: GraphSourceConfig | None = None,
    use_cache: bool = True,
) -> KnowledgeGraph:
    """Load the KnowledgeGraph from the highest-priority available source.

    Sources are tried in `config.priority` order and are NOT merged — the
    first one with data for `project` wins. Falls through to the UA loader
    (for its precise FileNotFoundError message) when nothing is available.
    """
    paths = resolve_project_paths(project)
    config = config or load_graph_source_config()

    for name in config.priority:
        source = _REGISTRY.get(name)
        if source is not None and source.available(paths.project_root):
            return source.load(paths.project_root, use_cache=use_cache)

    return load_knowledge_graph(paths.project_root, use_cache=use_cache)


def active_source_name(
    project: str | Path | None = None,
    *,
    config: GraphSourceConfig | None = None,
) -> str | None:
    """Name of the source `resolve_graph` would pick, or None if none is available."""
    paths = resolve_project_paths(project)
    config = config or load_graph_source_config()
    for name in config.priority:
        source = _REGISTRY.get(name)
        if source is not None and source.available(paths.project_root):
            return name
    return None
