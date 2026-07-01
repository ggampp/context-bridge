---
title: Workflow canônico doctor → sync → enrich
kind: convention
importance: 8
tags: workflow;operational
source_task: sprint-7-planning
---

# Workflow canônico

1. **Pós-`/understand`:** `context-bridge doctor` → `sync --incremental`
2. **Pré-tarefa:** `context-bridge enrich "<query>" --json --hops 1`
3. **Preview:** `suggest --dry-run` equivalente via `sync --dry-run` ou `suggest`

MCP: `bridge_doctor` → `sync_graph_to_engram(incremental=true)` → `enrich_memory_search`.

Sprint 7 formaliza em `workflows/` e estende `smoke.ps1`.
