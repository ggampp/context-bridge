from __future__ import annotations

from dataclasses import replace

from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.sync.engine import collect_payloads, run_sync
from context_bridge.sync.rules import load_sync_rules
from fakes import FakeEngramClient


def _small_graph_rules():
    """Fixture graph is tiny — lower hub threshold so mapper has output."""
    rules = load_sync_rules()
    return replace(rules, hubs=replace(rules.hubs, min_degree=2))


def test_collect_payloads_includes_all_mapper_types(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    rules = _small_graph_rules()
    payloads = collect_payloads(graph, rules, project="demo")
    types = {p.type for p in payloads}
    assert "architecture" in types  # layers
    assert "codebase-map" in types  # hubs


def test_collect_payloads_respects_types_filter(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    rules = load_sync_rules()
    payloads = collect_payloads(graph, rules, project="demo", types={"architecture"})
    assert payloads
    assert all(p.type == "architecture" for p in payloads)


def test_run_sync_dry_run_does_not_save(sample_project_root):
    report = run_sync(sample_project_root, dry_run=True)
    assert report.items
    assert all(item.status.startswith("would-") for item in report.items)
    assert not (sample_project_root / ".context-bridge" / "sync-state.json").exists()


def test_run_sync_creates_memories(sample_project_root):
    client = FakeEngramClient()
    report = run_sync(sample_project_root, client=client)
    assert report.items
    assert all(item.status == "created" for item in report.items)
    assert len(client.saved) == len(report.items)


def test_run_sync_writes_state_file(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client)
    state_file = sample_project_root / ".context-bridge" / "sync-state.json"
    assert state_file.exists()


def test_run_sync_second_run_skips_unchanged(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client)
    second_client = FakeEngramClient()
    report = run_sync(sample_project_root, client=second_client)
    assert all(item.status == "skipped" for item in report.items)
    assert not second_client.saved


def test_run_sync_force_reprocesses(sample_project_root):
    client = FakeEngramClient()
    run_sync(sample_project_root, client=client)
    second_client = FakeEngramClient()
    report = run_sync(sample_project_root, client=second_client, force=True)
    assert all(item.status == "created" for item in report.items)
    assert second_client.saved
