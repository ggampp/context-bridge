from __future__ import annotations

from context_bridge.sync.engine import run_sync
from context_bridge.sync.report import SyncItemResult, SyncReport, format_report
from fakes import FakeEngramClient


def _report() -> SyncReport:
    return SyncReport(
        items=[
            SyncItemResult(topic_key="cb-layer-api", title="api", type="architecture", status="created"),
            SyncItemResult(topic_key="cb-layer-web", title="web", type="architecture", status="skipped"),
            SyncItemResult(topic_key="cb-hub-router", title="router", type="codebase-map", status="created"),
        ],
        backend="http",
        graph_age_days=1.5,
        duration_seconds=0.25,
    )


def test_counts_by_type():
    report = _report()
    assert report.counts_by_type == {"architecture": 2, "codebase-map": 1}


def test_to_dict_includes_metrics():
    report = _report()
    data = report.to_dict()
    assert data["graph_age_days"] == 1.5
    assert data["duration_seconds"] == 0.25
    assert data["counts_by_type"] == {"architecture": 2, "codebase-map": 1}


def test_format_report_lists_counts_by_type():
    text = format_report(_report())
    assert "By type:" in text
    assert "architecture: 2" in text
    assert "codebase-map: 1" in text
    assert "graph age: 1.5d" in text
    assert "duration: 0.25s" in text


def test_format_report_graph_skipped_still_shows_metrics():
    report = SyncReport(items=[], graph_skipped=True, graph_age_days=3.0, duration_seconds=0.01)
    text = format_report(report)
    assert "Graph unchanged" in text
    assert "graph age: 3.0d" in text


def test_run_sync_populates_metrics(sample_project_root):
    client = FakeEngramClient()
    report = run_sync(sample_project_root, client=client)
    assert report.duration_seconds is not None and report.duration_seconds >= 0
    assert report.graph_age_days is not None and report.graph_age_days >= 0
    assert report.counts_by_type
