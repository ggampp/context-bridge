from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from context_bridge.graph.loader import clear_graph_cache


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def sample_project_root(tmp_path: Path, fixtures_dir: Path) -> Path:
    ua_dir = tmp_path / ".understand-anything"
    ua_dir.mkdir()
    graph_src = fixtures_dir / "graph_minimal.json"
    shutil.copy(graph_src, ua_dir / "knowledge-graph.json")
    (ua_dir / "config.json").write_text(
        json.dumps({"language": "en"}),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def lat_md_project_root(tmp_path: Path, fixtures_dir: Path) -> Path:
    """A project with only `lat.md/` (no `.understand-anything/`) — exercises the lat-md GraphSource."""
    shutil.copytree(fixtures_dir / "lat_md_minimal", tmp_path, dirs_exist_ok=True)
    return tmp_path


@pytest.fixture(autouse=True)
def _clear_graph_cache() -> None:
    clear_graph_cache()
    yield
    clear_graph_cache()
