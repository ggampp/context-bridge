from __future__ import annotations

from context_bridge.enrich.pipeline import EnrichResult
from context_bridge.hooks.post_sync import render_post_enrich_note, render_post_sync_note
from context_bridge.sync.report import SyncItemResult, SyncReport


def test_render_post_sync_note_graph_skipped():
    report = SyncReport(items=[], graph_skipped=True)
    note = render_post_sync_note(report)
    assert "already up to date" in note


def test_render_post_sync_note_dry_run_create():
    report = SyncReport(
        items=[SyncItemResult(topic_key="cb-x", title="X", type="architecture", status="would-create")]
    )
    note = render_post_sync_note(report)
    assert "Would sync 1 new" in note


def test_render_post_sync_note_real_create():
    report = SyncReport(items=[SyncItemResult(topic_key="cb-x", title="X", type="architecture", status="created")])
    note = render_post_sync_note(report)
    assert "Synced 1 new" in note


def test_render_post_sync_note_errors():
    report = SyncReport(
        items=[SyncItemResult(topic_key="cb-x", title="X", type="architecture", status="error", error="boom")]
    )
    note = render_post_sync_note(report)
    assert "failed to sync" in note


def test_render_post_sync_note_all_skipped():
    report = SyncReport(items=[SyncItemResult(topic_key="cb-x", title="X", type="architecture", status="skipped")])
    note = render_post_sync_note(report)
    assert "Nothing new to sync" in note


def test_render_post_enrich_note_no_memories():
    result = EnrichResult(query="x", memories=[], graph_available=True)
    note = render_post_enrich_note(result)
    assert "No memories matched" in note


def test_render_post_enrich_note_no_graph():
    from context_bridge.enrich.pipeline import EnrichedMemory
    from context_bridge.enrich.graph_context import GraphContextResult

    em = EnrichedMemory(memory={"title": "x"}, graph_context=GraphContextResult())
    result = EnrichResult(query="x", memories=[em], graph_available=False)
    note = render_post_enrich_note(result)
    assert "no Understand Anything graph" in note


def test_render_post_enrich_note_quiet_when_graph_available_and_memories_found():
    from context_bridge.enrich.pipeline import EnrichedMemory
    from context_bridge.enrich.graph_context import GraphContextResult

    em = EnrichedMemory(memory={"title": "x"}, graph_context=GraphContextResult())
    result = EnrichResult(query="x", memories=[em], graph_available=True)
    assert render_post_enrich_note(result) == ""
