from __future__ import annotations

from context_bridge.cli import main
from context_bridge.sync.engine import collect_payloads, run_sync
from context_bridge.sync.rules import load_sync_rules
from context_bridge.graph.loader import load_knowledge_graph
from fakes import FakeEngramClient


def test_dry_run_produces_expected_payload_count(sample_project_root):
    graph = load_knowledge_graph(sample_project_root)
    rules = load_sync_rules()
    expected = len(collect_payloads(graph, rules, project="demo"))

    report = run_sync(sample_project_root, dry_run=True)
    assert len(report.items) == expected
    assert expected > 0


def test_cli_sync_dry_run_exit_code(sample_project_root):
    code = main(["sync", "--project", str(sample_project_root), "--dry-run", "--json"])
    assert code == 0


def test_cli_sync_with_types_filter(sample_project_root):
    code = main(
        [
            "sync",
            "--project",
            str(sample_project_root),
            "--dry-run",
            "--types",
            "architecture",
            "--verbose",
        ]
    )
    assert code == 0


def test_e2e_dry_run_then_real_run_then_incremental_skip(sample_project_root):
    dry = run_sync(sample_project_root, dry_run=True)
    assert dry.items

    client = FakeEngramClient()
    real = run_sync(sample_project_root, client=client, incremental=True)
    assert len(real.items) == len(dry.items)
    assert all(i.status == "created" for i in real.items)

    second_client = FakeEngramClient()
    skipped = run_sync(sample_project_root, client=second_client, incremental=True)
    assert skipped.graph_skipped
