from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    id: str
    label: str = ""
    type: str = ""
    path: str = ""
    layer: str = ""
    summary: str = ""
    domain: str = ""
    language: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphNode:
        known = {"id", "label", "type", "path", "layer", "summary", "domain", "language"}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=str(data.get("id", "")),
            label=str(data.get("label", "")),
            type=str(data.get("type", "")),
            path=str(data.get("path", "")),
            layer=str(data.get("layer", "")),
            summary=str(data.get("summary", "")),
            domain=str(data.get("domain", "")),
            language=str(data.get("language", "")),
            extra=extra,
        )


@dataclass
class GraphEdge:
    source: str
    target: str
    type: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphEdge:
        known = {"source", "target", "type"}
        extra = {k: v for k, v in data.items() if k not in known}
        source = data.get("source") or data.get("from") or ""
        target = data.get("target") or data.get("to") or ""
        return cls(
            source=str(source),
            target=str(target),
            type=str(data.get("type", "")),
            extra=extra,
        )


@dataclass
class GraphConfig:
    language: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> GraphConfig:
        if not data:
            return cls()
        return cls(
            language=str(data.get("language", "")),
            raw=dict(data),
        )


@dataclass
class KnowledgeGraph:
    version: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    config: GraphConfig = field(default_factory=GraphConfig)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def node_by_id(self, node_id: str) -> GraphNode | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
