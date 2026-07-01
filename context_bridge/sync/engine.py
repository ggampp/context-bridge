from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from context_bridge.core.paths import resolve_project_paths
from context_bridge.engram.client import EngramClient
from context_bridge.engram.dedup import save_or_update
from context_bridge.engram.errors import EngramError
from context_bridge.engram.payloads import MemSavePayload
from context_bridge.graph.validate import validate_graph
from context_bridge.sources.resolver import active_source_name, default_graph_ref, graph_file_path, resolve_graph
from context_bridge.sync.incremental import graph_unchanged
from context_bridge.sync.mappers import map_domains, map_hubs, map_layers, map_tours
from context_bridge.sync.report import SyncItemResult, SyncReport
from context_bridge.sync.rules import SyncRules, load_sync_rules
from context_bridge.sync.state import SyncState, SyncStateEntry, compute_graph_hash, load_state, now_iso, save_state

_ALL_MAPPERS = {
    "architecture": map_layers,
    "codebase-map": map_hubs,
    "domain": map_domains,
    "tour": map_tours,
}


def _graph_age_days(graph_path: Path) -> float | None:
    if not graph_path.is_file():
        return None
    mtime = graph_path.stat().st_mtime
    age = datetime.now(tz=timezone.utc) - datetime.fromtimestamp(mtime, tz=timezone.utc)
    return age.total_seconds() / 86400


def collect_payloads(
    graph,
    rules: SyncRules,
    *,
    project: str | None = None,
    types: set[str] | None = None,
    graph_ref: str | None = None,
) -> list[MemSavePayload]:
    ref = graph_ref or rules.graph_ref or default_graph_ref(None)
    payloads: list[MemSavePayload] = []
    for mapper_type, mapper in _ALL_MAPPERS.items():
        if types and mapper_type not in types:
            continue
        if not rules.is_enabled(mapper_type):
            continue
        payloads.extend(mapper(graph, rules, project=project, graph_ref=ref))
    return payloads


def run_sync(
    project: str | Path | None = None,
    *,
    dry_run: bool = False,
    incremental: bool = False,
    force: bool = False,
    types: set[str] | None = None,
    rules: SyncRules | None = None,
    client: EngramClient | None = None,
) -> SyncReport:
    started = time.perf_counter()
    paths = resolve_project_paths(project)
    project_name = paths.project_root.name
    source_name = active_source_name(paths.project_root)
    graph_age_days = _graph_age_days(graph_file_path(paths.project_root, source_name))

    graph = resolve_graph(paths.project_root)
    validation = validate_graph(graph)
    if not validation.ok:
        errors = "; ".join(e.message for e in validation.errors)
        raise ValueError(f"Graph validation failed: {errors}")

    rules = rules or load_sync_rules()
    graph_ref = rules.graph_ref or default_graph_ref(source_name)
    state = load_state(paths.project_root)
    current_hash = compute_graph_hash(graph)

    if incremental and not force and graph_unchanged(graph, state):
        return SyncReport(
            items=[],
            graph_skipped=True,
            backend=None,
            graph_age_days=graph_age_days,
            duration_seconds=time.perf_counter() - started,
        )

    payloads = collect_payloads(graph, rules, project=project_name, types=types, graph_ref=graph_ref)

    backend_name: str | None = None
    if not dry_run:
        client = client or EngramClient()
        backend_name = client.backend

    results: list[SyncItemResult] = []
    new_entries: dict[str, SyncStateEntry] = dict(state.entries)

    for payload in payloads:
        existing = state.entries.get(payload.topic_key)
        unchanged_locally = (
            existing is not None and existing.content_hash == payload.content_hash and not force
        )

        if unchanged_locally:
            results.append(
                SyncItemResult(
                    topic_key=payload.topic_key,
                    title=payload.title,
                    type=payload.type,
                    status="skipped",
                    observation_id=existing.observation_id if existing else None,
                )
            )
            continue

        if dry_run:
            status = "would-update" if existing else "would-create"
            results.append(
                SyncItemResult(
                    topic_key=payload.topic_key,
                    title=payload.title,
                    type=payload.type,
                    status=status,
                    observation_id=existing.observation_id if existing else None,
                )
            )
            continue

        try:
            outcome = save_or_update(client, payload)
        except EngramError as e:
            results.append(
                SyncItemResult(
                    topic_key=payload.topic_key,
                    title=payload.title,
                    type=payload.type,
                    status="error",
                    error=str(e),
                )
            )
            continue

        results.append(
            SyncItemResult(
                topic_key=payload.topic_key,
                title=payload.title,
                type=payload.type,
                status=outcome.action,
                observation_id=outcome.observation_id,
            )
        )
        new_entries[payload.topic_key] = SyncStateEntry(
            content_hash=payload.content_hash,
            observation_id=outcome.observation_id,
            updated_at=now_iso(),
        )

    if not dry_run:
        save_state(SyncState(graph_hash=current_hash, entries=new_entries), paths.project_root)

    return SyncReport(
        items=results,
        graph_skipped=False,
        backend=backend_name,
        graph_age_days=graph_age_days,
        duration_seconds=time.perf_counter() - started,
    )
