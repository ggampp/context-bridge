from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "sync-rules.yaml"


@dataclass(frozen=True)
class LayerRules:
    enabled: bool = True
    min_nodes: int = 3


@dataclass(frozen=True)
class HubRules:
    enabled: bool = True
    min_degree: int = 5
    max_nodes: int = 20


@dataclass(frozen=True)
class DomainRules:
    enabled: bool = True
    min_nodes: int = 1


@dataclass(frozen=True)
class TourRules:
    enabled: bool = True
    max_tours: int = 3


# Default `where=` prefix for UA-sourced memories. Kept here (rather than
# duplicated per-mapper as `_UA_GRAPH_REL`) so sync/engine.py and the mappers
# share one source of truth; overridable via `sync-rules.yaml: graph_ref`
# or auto-detected per active graph source (see sources/resolver.py).
DEFAULT_GRAPH_REF = ".understand-anything/knowledge-graph.json"


@dataclass(frozen=True)
class SyncRules:
    version: int = 1
    layers: LayerRules = LayerRules()
    hubs: HubRules = HubRules()
    domains: DomainRules = DomainRules()
    tours: TourRules = TourRules()
    project_tag: str = "context-bridge"
    topic_key_prefix: str = "cb-"
    graph_ref: str = ""  # override for the `where=` prefix; "" = auto-detect per source

    def is_enabled(self, mapper_type: str) -> bool:
        return {
            "architecture": self.layers.enabled,
            "codebase-map": self.hubs.enabled,
            "domain": self.domains.enabled,
            "tour": self.tours.enabled,
        }.get(mapper_type, True)


def default_sync_rules() -> SyncRules:
    return SyncRules()


def load_sync_rules(path: str | Path | None = None) -> SyncRules:
    rules_path = Path(path) if path else _DEFAULT_RULES_PATH
    if not rules_path.is_file():
        return default_sync_rules()

    data = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    return SyncRules(
        version=int(data.get("version", 1)),
        layers=LayerRules(
            enabled=bool(data.get("layers", {}).get("enabled", True)),
            min_nodes=int(data.get("layers", {}).get("min_nodes", 3)),
        ),
        hubs=HubRules(
            enabled=bool(data.get("hubs", {}).get("enabled", True)),
            min_degree=int(data.get("hubs", {}).get("min_degree", 5)),
            max_nodes=int(data.get("hubs", {}).get("max_nodes", 20)),
        ),
        domains=DomainRules(
            enabled=bool(data.get("domains", {}).get("enabled", True)),
            min_nodes=int(data.get("domains", {}).get("min_nodes", 1)),
        ),
        tours=TourRules(
            enabled=bool(data.get("tours", {}).get("enabled", True)),
            max_tours=int(data.get("tours", {}).get("max_tours", 3)),
        ),
        project_tag=str(data.get("project_tag", "context-bridge")),
        topic_key_prefix=str(data.get("topic_key_prefix", "cb-")),
        graph_ref=str(data.get("graph_ref", "")),
    )
