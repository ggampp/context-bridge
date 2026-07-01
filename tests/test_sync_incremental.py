from __future__ import annotations

import json

from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.sync.engine import run_sync
from context_bridge.sync.incremental import graph_unchanged
from context_bridge.sync.state import compute_graph_hash, load_state
from fakes import FakeEngramClient


def test_incremental_skips_when_graph_unchanged(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client, incremental=True)

    second_client = FakeEngramClient()
    report = run_sync(sample_project_root, client=second_client, incremental=True)

    assert report.graph_skipped
    assert not second_client.saved


def test_incremental_runs_when_graph_changes(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client, incremental=True)

    graph_path = sample_project_root / ".understand-anything" / "knowledge-graph.json"
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    data["nodes"].append(
        {
            "id": "node-extra",
            "label": "extra.ts",
            "type": "file",
            "path": "src/extra.ts",
            "layer": "api",
        }
    )
    graph_path.write_text(json.dumps(data), encoding="utf-8")

    from context_bridge.graph.loader import clear_graph_cache

    clear_graph_cache()

    second_client = FakeEngramClient()
    report = run_sync(sample_project_root, client=second_client, incremental=True)

    assert not report.graph_skipped
    assert second_client.saved


def test_graph_unchanged_helper(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    state = load_state(sample_project_root)
    assert not graph_unchanged(graph, state)  # no prior state yet

    state.graph_hash = compute_graph_hash(graph)
    assert graph_unchanged(graph, state)


def test_no_duplicate_observations_across_runs(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client, force=True)
    first_count = len(client.saved)

    run_sync(sample_project_root, client=client, force=True)
    assert len(client.saved) == first_count
