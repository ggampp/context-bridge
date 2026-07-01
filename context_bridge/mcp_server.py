from __future__ import annotations

import json
import sys
from typing import Any

from context_bridge.doctor import run_checks
from context_bridge.engram.errors import EngramError
from context_bridge.enrich.format_json import format_json_dict
from context_bridge.enrich.pipeline import run_enrich
from context_bridge.suggest import build_suggestions
from context_bridge.sync.engine import run_sync

_INSTRUCTIONS = (
    "Bridges Understand Anything knowledge graphs to Engram persistent memory. "
    "Call bridge_doctor first to check prerequisites. Use sync_graph_to_engram "
    "(incremental=true) after running /understand to persist graph-derived "
    "memories. Use enrich_memory_search before starting a non-trivial task to "
    "pull in both past decisions and the relevant part of the codebase graph. "
    "Use suggest_memories_from_graph to preview what sync would write without "
    "touching Engram."
)


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def bridge_doctor_impl(project_path: str = ".") -> str:
    checks = run_checks(project_path)
    return _json([{"name": c.name, "status": c.status, "detail": c.detail} for c in checks])


def sync_graph_to_engram_impl(
    project_path: str = ".",
    dry_run: bool = False,
    incremental: bool = True,
    force: bool = False,
) -> str:
    try:
        report = run_sync(project_path, dry_run=dry_run, incremental=incremental, force=force)
    except (FileNotFoundError, ValueError, EngramError) as e:
        return _json({"error": str(e)})
    return _json(report.to_dict())


def enrich_memory_search_impl(
    query: str,
    project_path: str = ".",
    limit: int = 10,
    hops: int = 1,
) -> str:
    try:
        result = run_enrich(project_path, query, limit=limit, hops=hops)
    except (EngramError, FileNotFoundError, ValueError) as e:
        return _json({"error": str(e)})
    return _json(format_json_dict(result))


def suggest_memories_from_graph_impl(project_path: str = ".", types: str = "") -> str:
    type_set = {t.strip() for t in types.split(",") if t.strip()} or None
    try:
        payloads = build_suggestions(project_path, types=type_set)
    except (FileNotFoundError, ValueError) as e:
        return _json({"error": str(e)})
    return _json([p.to_dict() for p in payloads])


def run_mcp() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "MCP SDK not installed. Run: pip install context-bridge[mcp]",
            file=sys.stderr,
        )
        return 1

    mcp = FastMCP("context-bridge", instructions=_INSTRUCTIONS)

    @mcp.tool()
    def bridge_doctor(project_path: str = ".") -> str:
        """Check Engram backend reachability and Understand Anything graph status."""
        return bridge_doctor_impl(project_path)

    @mcp.tool()
    def sync_graph_to_engram(
        project_path: str = ".",
        dry_run: bool = False,
        incremental: bool = True,
        force: bool = False,
    ) -> str:
        """Sync the Understand Anything knowledge graph into Engram memories."""
        return sync_graph_to_engram_impl(project_path, dry_run, incremental, force)

    @mcp.tool()
    def enrich_memory_search(query: str, project_path: str = ".", limit: int = 10, hops: int = 1) -> str:
        """Search Engram memories enriched with related Understand Anything graph nodes."""
        return enrich_memory_search_impl(query, project_path, limit, hops)

    @mcp.tool()
    def suggest_memories_from_graph(project_path: str = ".", types: str = "") -> str:
        """Preview mem_save payloads derivable from the graph, without writing to Engram."""
        return suggest_memories_from_graph_impl(project_path, types)

    mcp.run()
    return 0
