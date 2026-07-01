from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from context_bridge.graph.models import KnowledgeGraph


@runtime_checkable
class GraphSource(Protocol):
    """A pluggable origin for a KnowledgeGraph (UA, lat.md, future adapters).

    Implementations decide their own on-disk layout; `resolver.py` only
    needs `available`/`load` to pick the highest-priority source that has
    data for a given project.
    """

    name: str

    def available(self, project_root: Path) -> bool:
        """Whether this source has usable data for `project_root`."""
        ...

    def load(self, project_root: Path, *, use_cache: bool = True) -> KnowledgeGraph:
        """Load (or build) the KnowledgeGraph for `project_root`."""
        ...
