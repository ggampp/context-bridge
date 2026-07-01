from __future__ import annotations

from context_bridge.cli import main
from context_bridge.doctor import run_checks
from context_bridge.enrich.graph_context import resolve_graph_context
from context_bridge.enrich.where_parser import parse_where
from context_bridge.sources.lat_md import lat_graph_path
from context_bridge.sources.resolver import resolve_graph
from context_bridge.sync.engine import run_sync
from fakes import FakeEngramClient


def test_sync_creates_domain_memories_from_lat_md(lat_md_project_root):
    client = FakeEngramClient()
    report = run_sync(lat_md_project_root, client=client)

    domain_items = [i for i in report.items if i.type == "domain"]
    assert {"cb-domain-auth", "cb-domain-billing"} <= {i.topic_key for i in domain_items}
    assert all(item.status == "created" for item in domain_items)

    saved_domain = next(rec for rec in client.saved.values() if rec["topic_key"] == "cb-domain-auth")
    assert "**Where**: .context-bridge/lat-graph.json#domain:" in saved_domain["content"]


def test_sync_dry_run_lat_md_does_not_write_state(lat_md_project_root):
    report = run_sync(lat_md_project_root, dry_run=True)
    assert report.items
    assert all(item.status == "would-create" for item in report.items)
    assert not (lat_md_project_root / ".context-bridge" / "sync-state.json").exists()


def test_enrich_resolves_lat_node_and_expands_one_hop(lat_md_project_root):
    resolve_graph(lat_md_project_root)  # ensure .context-bridge/lat-graph.json is built
    graph = resolve_graph(lat_md_project_root)

    parsed = parse_where(f"{lat_graph_path(lat_md_project_root).name}#node:lat-auth-oauth-flow")
    context = resolve_graph_context(parsed, graph, hops=1, limit=15)

    assert [n.id for n in context.anchor_nodes] == ["lat-auth-oauth-flow"]
    related_ids = {n.id for n in context.related_nodes}
    assert "lat-code-src-auth-ts-validatetoken" in related_ids
    assert "lat-billing-plan-limits" in related_ids


def test_cli_graph_import_lat_md_dry_run(lat_md_project_root):
    assert main(["graph", "import", "lat-md", "--project", str(lat_md_project_root), "--dry-run"]) == 0
    assert not lat_graph_path(lat_md_project_root).exists()


def test_cli_graph_import_lat_md_writes_file(lat_md_project_root):
    assert main(["graph", "import", "lat-md", "--project", str(lat_md_project_root)]) == 0
    assert lat_graph_path(lat_md_project_root).is_file()


def test_cli_graph_import_lat_md_custom_write_path(lat_md_project_root, tmp_path):
    out = tmp_path / "custom-graph.json"
    assert main(["graph", "import", "lat-md", "--project", str(lat_md_project_root), "--write", str(out)]) == 0
    assert out.is_file()


def test_doctor_reports_lat_md_present(lat_md_project_root):
    checks = run_checks(lat_md_project_root)
    lat_check = next(c for c in checks if c.name == "lat-md")
    assert lat_check.status == "OK"
    assert "2 domain file(s)" in lat_check.detail


def test_doctor_reports_lat_md_absent(sample_project_root):
    checks = run_checks(sample_project_root)
    lat_check = next(c for c in checks if c.name == "lat-md")
    assert lat_check.status == "OK"
    assert "not present" in lat_check.detail
