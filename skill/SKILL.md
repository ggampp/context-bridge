---
name: context-bridge
description: >
  Bridge between Understand Anything knowledge graphs and Engram persistent
  memory for coding agents. Auto-invoke when the user asks to sync the
  codebase graph with memory, enrich a memory search with codebase context,
  bridge engram and understand anything, persist graph-derived decisions, or
  mentions `/context-bridge`, `/sync-graph`, "sincronizar grafo com engram",
  "enriquecer memória com codebase".
metadata:
  short-description: "Understand Anything <-> Engram bridge via CLI + MCP"
---

# Context Bridge — UA ↔ Engram (v1.0)

## Quando usar (auto-trigger)

| Intenção do usuário | Ação imediata |
|---------------------|---------------|
| Sincronizar grafo UA com Engram | `bridge_doctor` → `sync_graph_to_engram` |
| Enriquecer busca de memória com contexto do código | `enrich_memory_search` |
| Ver o que seria salvo sem gravar | `suggest_memories_from_graph` |
| Checar se Engram/UA estão disponíveis | `bridge_doctor` |
| Configurar MCP no projeto | `context-bridge install --env=cursor` |
| `/context-bridge`, `/sync-graph` | Workflow completo abaixo |

**Não usar** para: rodar `/understand` (isso é do Understand Anything), gravar memórias manuais sem relação com o grafo (use Engram `mem_save` direto).

## Workflow recomendado

1. `bridge_doctor` (ou `context-bridge doctor`) — confirma Engram + grafo UA presentes.
2. Se o grafo existe e está OK → `sync_graph_to_engram(incremental=true)` — idempotente, seguro rodar sempre após `/understand`.
3. Antes de uma tarefa não-trivial → `enrich_memory_search(query)` — traz memórias Engram + nós do grafo relacionados (1 hop).
4. Decisões manuais que não vêm do grafo → Engram `mem_save` direto (não passa pelo bridge).
5. Quer só pré-visualizar o que o sync geraria, sem gravar? → `suggest_memories_from_graph`.

Passo a passo detalhado: [`workflows/sync-after-understand.md`](../workflows/sync-after-understand.md) (pós-`/understand`) e [`workflows/enrich-before-task.md`](../workflows/enrich-before-task.md) (pré-tarefa).

## `doctor` — WARN vs FAIL

`bridge_doctor` reporta cada check como `OK` / `WARN` / `FAIL`. Só `FAIL` bloqueia o workflow:

| Status | Significado | Ação do agent |
|--------|--------------|----------------|
| `OK` | Pronto para uso | Seguir o workflow normalmente |
| `WARN` | Dependência opcional ausente (Engram offline, grafo UA não gerado ainda) | Degradar graciosamente, não tratar como erro — ex.: `sync --dry-run` funciona sem Engram; `enrich` sem grafo ainda retorna memórias, só sem contexto de código |
| `FAIL` | Python < 3.10, grafo corrompido | Parar e reportar ao usuário antes de continuar |

`enrich`/`sync` sem Engram alcançável retornam um erro explícito (não silencioso) — trate como `WARN` operacional, não como falha do agent.

## Ferramentas MCP

| Tool | Input | Output |
|------|-------|--------|
| `bridge_doctor` | `project_path?` | JSON com status de Python, Engram, diretório UA, grafo |
| `sync_graph_to_engram` | `project_path?`, `dry_run?`, `incremental?`, `force?` | Relatório de sync (created/updated/skipped/error) |
| `enrich_memory_search` | `query`, `project_path?`, `limit?`, `hops?` | JSON v1: `{ query, memories[], graph_nodes[] }` |
| `suggest_memories_from_graph` | `project_path?`, `types?` | Lista de payloads `mem_save` (sem gravar) |

## Comandos CLI equivalentes

```bash
context-bridge doctor
context-bridge sync --incremental
context-bridge sync --dry-run --verbose
context-bridge enrich "fluxo de autenticação" --json
context-bridge suggest --types architecture,domain --json
context-bridge install --env=cursor
context-bridge mcp   # servidor MCP stdio
```

## MCP Server

Instalar: `pip install -e ".[mcp]"` (ou `pip install context-bridge[mcp]`)

Configurar em `.cursor/mcp.json` (gerado automaticamente por `context-bridge install --env=cursor`):

```json
{
  "mcpServers": {
    "context-bridge": {
      "command": "context-bridge",
      "args": ["mcp"]
    }
  }
}
```

Engram (`mem_save`, `mem_search`) é complementar — o bridge não substitui o MCP nativo do Engram, apenas conecta o grafo UA a ele.

## Regras de execução

1. **Sempre rodar `bridge_doctor` primeiro** se o estado do projeto for desconhecido.
2. **`sync` é idempotente** — usar `--incremental` no dia a dia; `--force` só quando o estado local parecer corrompido.
3. **`enrich` antes de tarefas grandes** — evita repetir decisões já documentadas no Engram.
4. **`suggest` não tem efeitos colaterais** — seguro chamar quantas vezes quiser.
5. **Memórias sem `where`** ainda aparecem no `enrich`; o contexto de grafo é omitido com uma nota.

## Slash commands

- `/context-bridge` — roda o workflow completo (doctor → sync → enrich)
- `/sync-graph` — alias para `sync_graph_to_engram`

## Workflows detalhados

`context-bridge/workflows/sync-after-understand.md` e `context-bridge/workflows/enrich-before-task.md`
