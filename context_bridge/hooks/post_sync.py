from __future__ import annotations

from context_bridge.enrich.pipeline import EnrichResult
from context_bridge.sync.report import SyncReport

# Mirrors agent-reach-tech's hooks/post_research.py pattern: a short,
# optional markdown block appended after a CLI/MCP action to nudge the
# agent toward the next useful step in the Engram workflow.


def render_post_sync_note(report: SyncReport) -> str:
    if report.graph_skipped:
        return (
            "\n---\n\n### Context Bridge\n"
            "Graph unchanged since the last sync — Engram memory is already up to date.\n"
        )

    counts = report.counts
    created = counts.get("created", 0) + counts.get("would-create", 0)
    updated = counts.get("updated", 0) + counts.get("would-update", 0)
    errors = counts.get("error", 0)
    dry_run = "would-create" in counts or "would-update" in counts or "would-skip" in counts

    if errors:
        return (
            "\n---\n\n### Context Bridge\n"
            f"{errors} item(s) failed to sync. Run `context-bridge doctor` to check the Engram backend.\n"
        )

    if created or updated:
        verb = "Would sync" if dry_run else "Synced"
        return (
            "\n---\n\n### Context Bridge\n"
            f"{verb} {created} new and {updated} updated memories from the knowledge graph.\n"
            'Next: run `context-bridge enrich "<task>"` before starting work to pull in graph context.\n'
        )

    return (
        "\n---\n\n### Context Bridge\n"
        "Nothing new to sync — all mapped memories were already up to date.\n"
    )


def render_post_enrich_note(result: EnrichResult) -> str:
    if not result.memories:
        return (
            "\n---\n\n### Context Bridge\n"
            "No memories matched this query yet. Consider running `context-bridge sync` first, "
            "or save a decision directly via Engram's `mem_save`.\n"
        )
    if not result.graph_available:
        return (
            "\n---\n\n### Context Bridge\n"
            "Returned Engram memories only — no Understand Anything graph found in this project "
            "(run `/understand` to enable graph context).\n"
        )
    return ""
