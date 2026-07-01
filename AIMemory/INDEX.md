# AIMemory — Índice (context-bridge)

Memória do subprojeto **context-bridge**. Leia:

1. `PROJECT_OVERVIEW.md`
2. Tail de `work.log`
3. Handoffs abertos
4. `knowledge/`

Monorepo pai: `../../AIMemory/` · handoff v1x planning fechado lá (2026-07-01).

## Inventário

| Arquivo | Função |
|---------|--------|
| `PROJECT_OVERVIEW.md` | Onboarding bridge grafo↔Engram |
| `work.log` | Eventos append-only |
| `handoffs/` | Handoffs de implementação |
| `knowledge/` | Decisões de arquitetura |
| `archive/` | Histórico frio |

## Handoffs ativos

*(nenhum — v1.x concluído)*

| Arquivo | Task | Status |
|---------|------|--------|
| Ver também | `../../AIMemory/handoffs/2026-06-30-context-bridge-v1x-planning.md` | **fechado** — v1.2.0 |

## Índice de tópicos

| Tópico | Onde |
|--------|------|
| workflow pós-/understand | `workflows/sync-after-understand.md` |
| enrich pré-tarefa | `workflows/enrich-before-task.md` |
| schema grafo | `context_bridge/graph/models.py`, `tests/fixtures/graph_minimal.json` |
| sync incremental | `sync/engine.py`, `.context-bridge/sync-state.json` |
| multi-fonte | `docs/SOURCES.md`, `context_bridge/sources/` |
| adapter lat.md | `context_bridge/sources/lat_md/`, `docs/adr/003-lat-md-semantic-source.md` |
| adapters externos (defer) | `docs/research/watchlist.md`, ADR 004/005 |
| backlog v1.3+ | `CHANGELOG.md` (Unreleased), `docs/PLANO-SPRINTS.md` |

## Conhecimento promovido

| Título | Arquivo |
|--------|---------|
| Thin bridge — limites | [knowledge/thin-bridge-limits.md](knowledge/thin-bridge-limits.md) |
| UA fonte primária | [knowledge/ua-primary-source.md](knowledge/ua-primary-source.md) |
| Workflow canônico | [knowledge/canonical-workflow.md](knowledge/canonical-workflow.md) |

## Sprints

| Sprint | Status | Versão |
|--------|--------|--------|
| 0–6 | concluída | v1.0.0 |
| 7 | concluída | v1.0.1 |
| 8 | concluída | v1.1.0 |
| 9 | concluída | v1.1.1 |
| 10 | concluída | v1.2.0 |

Detalhe: `docs/PLANO-SPRINTS.md`