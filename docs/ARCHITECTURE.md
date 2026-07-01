# Architecture — Context Bridge

## Overview

```
                         ┌────────────────────────┐
   /understand   ──────▶ │ .understand-anything/   │
                         │   knowledge-graph.json  │
                         │   config.json           │
                         │   diff-overlay.json     │
                         └───────────┬─────────────┘
                                     │ read-only
                                     ▼
                         ┌────────────────────────┐
   CLI / MCP    ───────▶ │     context-bridge      │ ◀─────  agents
                         │  doctor·sync·enrich·    │         (Cursor, Claude
                         │  suggest·install·mcp    │          Code, Codex...)
                         └───────────┬─────────────┘
                                     │ HTTP (preferred) or CLI fallback
                                     ▼
                         ┌────────────────────────┐
                         │         Engram          │
                         │  mem_save / mem_search  │
                         └────────────────────────┘
```

`context-bridge` never writes to `.understand-anything/*.json` and never
substitutes Engram's own MCP server — it is a thin, idempotent translation
layer between the two.

## Modules

| Module | Responsibility |
|--------|-----------------|
| `core/` | `ProjectPaths` resolution, subprocess runner — shared utilities |
| `graph/` | Typed models (`GraphNode`, `GraphEdge`, `KnowledgeGraph`), JSON loader with caching, validation, queries (layers, hubs, domains, neighbors), diff overlay |
| `engram/` | `EngramClient` facade — HTTP backend (`engram serve`) with CLI fallback (`engram` binary); `MemSavePayload` contract; dedup by `topic_key` |
| `sync/` | YAML-configurable rules, mappers (graph → `MemSavePayload`), incremental state (`.context-bridge/sync-state.json`), engine, human/JSON report |
| `enrich/` | `where` parser (anchors + bare paths), graph context resolver (BFS neighbors), hybrid search pipeline, markdown/JSON formatters |
| `suggest.py` | Read-only preview of sync payloads (reuses `sync` mappers, no writes) |
| `hooks/` | Optional markdown notes appended after `sync`/`enrich` to nudge the next agent action |
| `core/installer.py` | Detects project, writes/merges `.cursor/mcp.json`, checks optional deps |
| `mcp_server.py` | FastMCP server exposing the same operations as MCP tools |
| `cli.py` | `argparse` entrypoint wiring all of the above |

## Flows

### Post-`/understand` sync

1. Agent runs `/understand` → `.understand-anything/knowledge-graph.json` is created/updated.
2. `context-bridge sync --incremental` (or MCP `sync_graph_to_engram`):
   - Loads + validates the graph.
   - Computes a graph hash; if unchanged and `--incremental`, skips entirely.
   - Runs enabled mappers (`architecture`, `codebase-map`, `domain`, `tour`) to build `MemSavePayload`s.
   - For each payload: skip if content hash unchanged locally; otherwise save/update via `EngramClient`, using `topic_key` to upsert and avoid duplicates remotely.
   - Persists new sync state (graph hash + per-topic_key content hash + observation id).

### Pre-task enrich

1. Agent calls `context-bridge enrich "<task>"` (or MCP `enrich_memory_search`).
2. `EngramClient.search(query)` returns matching memories.
3. For each memory, the `**Where**` line in its content is parsed:
   - context-bridge anchors (`#layer:`, `#node:`, `#domain:`, `#tours`) resolve directly to graph nodes.
   - Bare file paths (manually-written memories) resolve via path matching.
4. Anchor nodes are expanded by `hops` (default 1) over graph edges (treated as undirected) to surface related files.
5. Result is rendered as markdown (agent-friendly) or a versioned JSON schema.

Both flows degrade gracefully when the *graph* is missing: `enrich` still returns Engram memories with graph context omitted (and a note). `sync --dry-run` and `suggest` work fully offline regardless of Engram. A live Engram backend is required for `sync` (non-dry-run) and `enrich` to actually save/search — if it's unreachable, both report an explicit error (CLI exit 1 / MCP `{"error": ...}`) rather than failing silently; `doctor` surfaces this ahead of time as `WARN`, not `FAIL` (see below).

## Operational flow (post-v1.0)

The canonical day-to-day loop, formalized in Sprint 7:

| Phase | Command / MCP tool | When | Side effects |
|-------|---------------------|------|---------------|
| Pre-flight | `doctor` / `bridge_doctor` | Before sync | None |
| Post-`/understand` | `sync --incremental` | Graph created/updated | Upserts Engram |
| Pre-task | `enrich "<query>"` | Before editing a module | None |
| Preview | `suggest` | Debug / onboarding | None |

Step-by-step recipes: [`workflows/sync-after-understand.md`](../workflows/sync-after-understand.md) and [`workflows/enrich-before-task.md`](../workflows/enrich-before-task.md).

`doctor` reports each check as `OK` / `WARN` / `FAIL`. Only `FAIL` (Python < 3.10, a corrupt graph) should stop an agent — `WARN` (Engram unreachable, UA graph not generated yet) is an expected degraded state the other commands already handle. `scripts/smoke.ps1` mirrors this: every step is a hard failure except `enrich`, which only warns when Engram is unreachable.

`sync`'s report (`SyncReport`) now also carries operational metrics: `graph_age_days` (time since `knowledge-graph.json` was last modified), `duration_seconds` (wall-clock time of the sync run), and a per-mapper-type breakdown (`counts_by_type`, e.g. `architecture`/`codebase-map`/`domain`/`tour`) alongside the existing per-status counts.

## Config

| File | Purpose |
|------|---------|
| `config/sync-rules.yaml` | Which mappers run, thresholds (`min_degree`, `min_nodes`, limits) |
| `config/mcp.json` | Template MCP server entry for Cursor/Claude/other clients |
| `.context-bridge/sync-state.json` (generated, per-project) | Incremental sync state — graph hash + topic_key → content hash/observation id |

## Tests

- Offline (default `pytest`): fixtures (`tests/fixtures/graph_minimal.json`) + `FakeEngramClient` (`tests/fakes.py`) — no network, no real Engram process required.
- `@pytest.mark.network` (`tests/test_integration_network.py`): opt-in tests against a live Engram backend, self-skip when unreachable. Run with `pytest -m network`.
- `tests/test_integration_e2e.py`: full CLI/engine flow (doctor → sync → enrich → suggest) using the offline fakes.
