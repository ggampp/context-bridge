# Context Bridge

Ponte entre fontes de grafo de conhecimento — **Understand Anything** (estrutural) ou **lat.md** (semântico) — e **Engram** (memória persistente entre sessões).

**Status:** v1.2.0 entregue (sprints 0–10 concluídas). Backlog pós-v1.2: merge UA+lat.md (v1.3), reavaliar adapters Orbit KG/Potpie. Ver [docs/PLANO-SPRINTS.md](docs/PLANO-SPRINTS.md), [CHANGELOG.md](CHANGELOG.md) e [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md).

## O que faz

```
.understand-anything/knowledge-graph.json  ─┐
lat.md/*.md + anotações @lat:              ─┼→  context-bridge (CLI / MCP)
                                            │         ↓
                                            │   Engram (mem_save / mem_search)
                                            │         ↓
                                            └──→  Cursor, Claude Code, Codex, etc.
```

- **Sync** — converte camadas, domínios e nós centrais do grafo em memórias Engram estruturadas, com dedup via `topic_key` e estado incremental
- **Enrich** — busca híbrida: memórias Engram + nós do grafo relacionados (1+ hops)
- **Suggest** — pré-visualiza payloads `mem_save` do grafo, sem gravar nada
- **Doctor** — valida Python, backend Engram (HTTP/CLI) e fontes de grafo (UA, lat.md)
- **MCP** — expõe as 4 operações acima como tools para agents
- **Install** — gera/mescla `.cursor/mcp.json` e verifica dependências opcionais

Fontes plugáveis via `context_bridge/sources/` — ver [docs/SOURCES.md](docs/SOURCES.md). A primeira fonte disponível em `config/graph-source.yaml` vence (sem merge entre UA e lat.md).

## Instalação

```powershell
cd context-bridge
pip install -e ".[dev]"        # CLI + testes
pip install -e ".[mcp]"        # + servidor MCP (FastMCP)
```

Verificar:

```powershell
pytest -m "not network"
context-bridge doctor
.\scripts\smoke.ps1
```

## Comandos

```powershell
context-bridge doctor                                  # status Python/Engram/fontes de grafo
context-bridge sync [--dry-run] [--incremental] [--force] [--types t1,t2] [--json] [--verbose]
context-bridge enrich "fluxo de pagamento" [--json] [--hops 1] [--limit 10] [--node-limit 15]
context-bridge suggest [--types architecture,domain] [--json]
context-bridge graph stats|node <id|path> [--json]
context-bridge graph import lat-md [--dry-run] [--write PATH]
context-bridge install --env=cursor [--dry-run] [--force]
context-bridge mcp                                      # servidor MCP via stdio
```

## Workflow recomendado

1. **Pós-`/understand`** — sempre que o grafo UA for gerado/atualizado: `doctor` → `sync --incremental`. Receita completa em [workflows/sync-after-understand.md](workflows/sync-after-understand.md).
2. **Com lat.md** — após atualizar `lat.md/` ou anotações `@lat:`: `graph import lat-md` (se necessário) → `sync --incremental`.
3. **Pré-tarefa** — antes de editar um módulo não-trivial: `enrich "<query>"` para trazer memórias Engram + contexto de grafo relacionado. Receita completa em [workflows/enrich-before-task.md](workflows/enrich-before-task.md).

`doctor` nunca falha (`FAIL`) por Engram ou grafo ausentes — esses casos viram `WARN` e os comandos degradam graciosamente (`sync --dry-run` funciona offline; `enrich` sem grafo retorna memórias sem contexto de código).

## Matriz de features

| Feature | Funciona sem Engram? | Funciona sem grafo? | Side effects |
|---------|----------------------|---------------------|--------------|
| `doctor` | Sim (reporta WARN) | Sim (reporta WARN) | Nenhum |
| `sync --dry-run` | Sim | Não (precisa do grafo) | Nenhum |
| `sync` | Não | Não | Grava/atualiza memórias Engram |
| `enrich` | Não (precisa buscar) | Sim (memórias sem contexto de grafo) | Nenhum |
| `suggest` | Sim | Não | Nenhum |
| `install` | Sim | Sim | Escreve `.cursor/mcp.json` |
| `mcp` | Sim (tools degradam graciosamente) | Sim | Depende da tool chamada |

## Dependências

| Dependência | Obrigatória? | Uso |
|-------------|--------------|-----|
| Python ≥ 3.10 | Sim | Runtime |
| `pyyaml` | Sim | `config/sync-rules.yaml`, `config/graph-source.yaml` |
| `pytest`, `pytest-cov` (`[dev]`) | Apenas dev | Testes (180+ offline) |
| `mcp` ≥ 1.2.0 (`[mcp]`) | Apenas para `context-bridge mcp` | Servidor MCP (FastMCP) |
| [Engram](https://github.com/Gentleman-Programming/engram) (binário Go) | Não (degrada para WARN) | Backend de memória — HTTP (`engram serve`) ou CLI |
| [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) | Não (degrada para WARN) | Gera `.understand-anything/knowledge-graph.json` |
| [lat.md](https://github.com/1st1/lat.md) | Não (segunda fonte) | Grafo semântico em `lat.md/`; CLI `lat` opcional |

## Histórico de versões (resumo)

| Versão | Sprint | Destaque |
|--------|--------|----------|
| v1.0.0 | 0–6 | Sync, enrich, suggest, doctor, MCP |
| v1.0.1 | 7 | Workflows, smoke `enrich`, métricas sync |
| v1.1.0 | 8 | Adapter lat.md (`sources/lat_md/`) |
| v1.1.1 | 9 | Catálogo lat.md/Potpie no monorepo |
| v1.2.0 | 10 | Spikes Orbit KG + Potpie → defer |

Detalhe completo em [CHANGELOG.md](CHANGELOG.md).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md) | Visão geral, stack, princípios de design |
| [PLANO-SPRINTS.md](docs/PLANO-SPRINTS.md) | Sprints 0–10 (concluídas) + backlog v1.3 |
| [SOURCES.md](docs/SOURCES.md) | Multi-fonte: UA, lat.md, limitações |
| [sprints/](docs/sprints/) | Detalhamento tarefa a tarefa por sprint |
| [research/watchlist.md](docs/research/watchlist.md) | Candidatos a adapter; Orbit/Potpie em defer |
| [research/go-no-go-adapters.md](docs/research/go-no-go-adapters.md) | Critério adopt/defer/reject |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Módulos, fluxos sync/enrich, config, testes |
| [MCP-SETUP.md](docs/MCP-SETUP.md) | Setup do servidor MCP no Cursor e outros clientes |
| [skill/SKILL.md](skill/SKILL.md) | Auto-trigger e workflow para agents |
| [workflows/](workflows/) | Receitas pós-`/understand` e pré-tarefa |

## MCP

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

Gerar automaticamente: `context-bridge install --env=cursor`. Detalhes em [docs/MCP-SETUP.md](docs/MCP-SETUP.md).

## Testes

```powershell
pytest                        # offline + network tests auto-skip
pytest -m "not network"       # explicitamente offline (usado no CI) — 180+ testes
pytest -m network             # apenas contra Engram real (precisa de backend rodando)
.\scripts\smoke.ps1           # doctor + sync --dry-run + suggest + enrich + graph stats
```

## Relacionados

- [Engram](https://github.com/Gentleman-Programming/engram) — memória persistente (Go, MCP)
- [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) — grafo estrutural do codebase
- [lat.md](https://github.com/1st1/lat.md) — grafo semântico em Markdown (segunda fonte)
- [Agent Reach Tech](../agent-reach-tech/) — research externo → Engram (padrão de hooks/MCP seguido aqui)

## Licença

MIT — ver [LICENSE](LICENSE)