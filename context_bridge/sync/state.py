from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from context_bridge.graph.models import KnowledgeGraph

_STATE_FILENAME = "sync-state.json"
_STATE_DIRNAME = ".context-bridge"


@dataclass
class SyncStateEntry:
    content_hash: str
    observation_id: int | str | None
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "observation_id": self.observation_id,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SyncStateEntry:
        return cls(
            content_hash=str(data.get("content_hash", "")),
            observation_id=data.get("observation_id"),
            updated_at=str(data.get("updated_at", "")),
        )


@dataclass
class SyncState:
    graph_hash: str = ""
    entries: dict[str, SyncStateEntry] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_hash": self.graph_hash,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SyncState:
        entries = {
            k: SyncStateEntry.from_dict(v)
            for k, v in (data.get("entries") or {}).items()
            if isinstance(v, dict)
        }
        return cls(graph_hash=str(data.get("graph_hash", "")), entries=entries)


def state_path(project_root: str | Path) -> Path:
    return Path(project_root) / _STATE_DIRNAME / _STATE_FILENAME


def load_state(project_root: str | Path) -> SyncState:
    path = state_path(project_root)
    if not path.is_file():
        return SyncState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return SyncState()
    if not isinstance(data, dict):
        return SyncState()
    return SyncState.from_dict(data)


def save_state(state: SyncState, project_root: str | Path) -> None:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def compute_graph_hash(graph: KnowledgeGraph) -> str:
    """Stable fingerprint of graph content, used to skip unchanged syncs."""
    node_keys = sorted(f"{n.id}:{n.path}:{n.layer}:{n.domain}" for n in graph.nodes)
    edge_keys = sorted(f"{e.source}->{e.target}:{e.type}" for e in graph.edges)
    payload = json.dumps({"v": graph.version, "n": node_keys, "e": edge_keys}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
