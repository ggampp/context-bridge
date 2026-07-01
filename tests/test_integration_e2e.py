from __future__ import annotations

from fakes import FakeEngramClient

from context_bridge.cli import main
from context_bridge.doctor import run_checks
from context_bridge.enrich.pipeline import run_enrich
from context_bridge.suggest import build_suggestions
from context_bridge.sync.engine import run_sync


class SearchableFakeEngramClient(FakeEngramClient):
    """Extends the sync fake with a richer `search` for enrich integration tests."""

    def search(self, query, project=None, limit=10):
        results = []
        for obs_id, rec in self.saved.items():
            haystack = f"{rec['topic_key']} {rec['content']}".lower()
            if query.lower() in haystack:
                results.append(
                    {
                        "id": obs_id,
                        "title": rec["topic_key"],
                        "type": "unknown",
                        "topic_key": rec["topic_key"],
                        "content": rec["content"],
                    }
                )
        return results[:limit]


def test_doctor_reports_graph_present_engram_absent(sample_project_root):
    checks = run_checks(sample_project_root)
    by_name = {c.name: c for c in checks}
    assert by_name["knowledge-graph"].status == "OK"
    assert by_name["engram"].status in {"OK", "WARN"}


def test_full_pipeline_sync_then_enrich(sample_project_root):
    client = SearchableFakeEngramClient()

    first = run_sync(sample_project_root, client=client)
    assert first.counts.get("created", 0) >= 1
    assert first.counts.get("error", 0) == 0

    second = run_sync(sample_project_root, client=client)
    assert second.counts.get("created", 0) == 0
    assert second.counts.get("updated", 0) == 0
    assert second.counts.get("skipped", 0) == first.counts.get("created", 0) + first.counts.get("updated", 0)

    enrich_result = run_enrich(sample_project_root, "layer", client=client)
    assert enrich_result.graph_available
    assert enrich_result.memories
    matched = [m for m in enrich_result.memories if not m.graph_context.is_empty]
    assert matched, "expected at least one memory to resolve graph context"


def test_suggest_matches_sync_payload_count(sample_project_root):
    client = FakeEngramClient()
    sync_report = run_sync(sample_project_root, client=client)
    suggestions = build_suggestions(sample_project_root)
    synced_count = sum(sync_report.counts.get(s, 0) for s in ("created", "updated", "skipped"))
    assert len(suggestions) == synced_count


def test_cli_doctor_sync_suggest_flow(sample_project_root):
    assert main(["doctor", "--project", str(sample_project_root)]) in (0, 1)
    assert main(["sync", "--project", str(sample_project_root), "--dry-run", "--json"]) == 0
    assert main(["suggest", "--project", str(sample_project_root), "--json"]) == 0
    assert main(["graph", "stats", "--project", str(sample_project_root), "--json"]) == 0
