from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from context_bridge.core.paths import ProjectPaths, resolve_project_paths


@dataclass
class DiffOverlay:
    changed_paths: list[str] = field(default_factory=list)
    added_node_ids: list[str] = field(default_factory=list)
    removed_node_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_paths or self.added_node_ids or self.removed_node_ids)


def load_diff_overlay(project: str | Path | None = None) -> DiffOverlay | None:
    paths = resolve_project_paths(project)
    return load_diff_overlay_from_paths(paths)


def load_diff_overlay_from_paths(paths: ProjectPaths) -> DiffOverlay | None:
    path = paths.diff_overlay
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None

    changed = data.get("changedPaths") or data.get("changed_paths") or []
    added = data.get("addedNodeIds") or data.get("added_node_ids") or []
    removed = data.get("removedNodeIds") or data.get("removed_node_ids") or []

    return DiffOverlay(
        changed_paths=[str(p) for p in changed] if isinstance(changed, list) else [],
        added_node_ids=[str(n) for n in added] if isinstance(added, list) else [],
        removed_node_ids=[str(n) for n in removed] if isinstance(removed, list) else [],
        raw=data,
        source_path=str(path),
    )
