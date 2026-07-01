from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    project_root: Path
    ua_dir: Path
    knowledge_graph: Path
    ua_config: Path
    diff_overlay: Path
    engram_data_dir: Path

    @property
    def has_ua_dir(self) -> bool:
        return self.ua_dir.is_dir()

    @property
    def has_knowledge_graph(self) -> bool:
        return self.knowledge_graph.is_file()


def resolve_project_paths(project: str | Path | None = None) -> ProjectPaths:
    root = Path(project or os.getcwd()).resolve()
    ua_dir = root / ".understand-anything"
    engram_home = Path(os.environ.get("ENGRAM_DATA_DIR", Path.home() / ".engram"))
    return ProjectPaths(
        project_root=root,
        ua_dir=ua_dir,
        knowledge_graph=ua_dir / "knowledge-graph.json",
        ua_config=ua_dir / "config.json",
        diff_overlay=ua_dir / "diff-overlay.json",
        engram_data_dir=engram_home,
    )
