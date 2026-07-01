# Desenvolvimento — Context Bridge

**Objetivo:** conectar o grafo do Understand Anything à memória do Engram, para que coding agents tenham **estrutura do código** e **decisões aprendidas** no mesmo fluxo de trabalho.

**Nome do pacote:** `context-bridge`  
**CLI:** `context-bridge`  
**Módulo Python:** `context_bridge`  
**Licença:** MIT

---

## Problema que resolve

| Ferramenta | Guarda | Lacuna |
|------------|--------|--------|
| Understand Anything | O que o código *é* (nós, arestas, camadas) | Não persiste entre projetos/sessões como memória de agent |
| Engram | O que o agent *aprendeu* (decisões, bugfixes) | Não conhece a topologia do codebase |

Hoje o agente precisa fazer a ponte manualmente. O Context Bridge automatiza essa ponte lendo o JSON do UA e gravando/consultando via Engram.

---

## Princípios de design

1. **Thin bridge** — não reimplementa `/understand`; consome `.understand-anything/*.json`
2. **Engram-first** — usa HTTP API (`engram serve`) com fallback CLI (`engram save/search`)
3. **Referência, não cópia** — memórias Engram apontam para paths/nós do grafo; não duplica o grafo inteiro
4. **Incremental** — sync detecta diff no grafo e só atualiza o que mudou
5. **Agent-ready** — CLI + MCP + skill (mesmo padrão do agent-reach-tech)

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Runtime | Python ≥ 3.10 |
| CLI | argparse / typer (seguir agent-reach-tech) |
| HTTP | urllib ou httpx (Engram REST em `:7437`) |
| Config | YAML + `.understand-anything/config.json` |
| MCP | FastMCP (extra `[mcp]`) |
| Testes | pytest + fixtures JSON |

**Dependências externas (runtime):**

- `engram` — binário Go instalado (`engram setup cursor`)
- Understand Anything — grafo gerado em `.understand-anything/` (comando `/understand`)

---

## Produto final (v1.0)

```
context-bridge/
├── context_bridge/
│   ├── cli.py              → entrypoint
│   ├── doctor.py           → probes Engram + UA graph
│   ├── graph/              → loader, models, queries
│   ├── engram/             → client HTTP + CLI fallback
│   ├── sync/               → mapeamento grafo → mem_save
│   ├── enrich/             → mem_search + contexto do grafo
│   ├── hooks/              → pós-/understand suggestions
│   └── mcp_server.py       → MCP tools (extra)
├── config/
│   ├── sync-rules.yaml     → o que sincronizar (layers, domains, hubs)
│   └── mcp.json            → template Cursor
├── skill/SKILL.md          → auto-trigger no Cursor
├── tests/                  → offline + @network
└── docs/
```

### Comandos alvo

```powershell
context-bridge doctor
context-bridge sync [--dry-run] [--incremental]
context-bridge enrich "auth flow" [--json]
context-bridge suggest                    # payloads mem_save sem gravar
context-bridge mcp                        # servidor MCP
context-bridge install --env=auto         # skill + deps check
```

### MCP tools alvo

| Tool | Função |
|------|--------|
| `bridge_doctor` | Status Engram + grafo UA |
| `sync_graph_to_engram` | Sync incremental |
| `enrich_memory_search` | Busca Engram + nós relacionados |
| `suggest_memories_from_graph` | Payloads mem_save a partir do grafo |

---

## Definition of Done (projeto v1.0)

- [x] `context-bridge doctor` valida Engram + `.understand-anything/knowledge-graph.json`
- [x] `context-bridge sync` grava memórias tipadas no Engram sem duplicar (topic_key)
- [x] `context-bridge enrich` retorna contexto híbrido (memória + grafo)
- [x] MCP com 4 tools funcional no Cursor
- [x] Skill auto-trigger documentada
- [x] Testes offline passam (`pytest`); testes `@network` opcionais
- [x] README permite onboarding em < 10 min
- [x] Entrada no catálogo `manifests/projects.json` do repositório pai

**v1.0.0 entregue.** Ver [CHANGELOG.md](../CHANGELOG.md) para o histórico completo por sprint.

**v1.x em planejamento.** Sprints 7–10 cobrem operacionalização UA, adapter lat.md, catálogo/watchlist e research spikes (Orbit KG / Potpie). Ver [PLANO-SPRINTS.md](PLANO-SPRINTS.md#índice-das-sprints--v1x-evolução).

---

## Sprints

### v1.0 (concluídas)

| Sprint | Nome | Duração | Entrega principal | Status |
|--------|------|---------|-------------------|--------|
| [0](sprints/sprint-0-fundacao.md) | Fundação | 2–3 dias | Scaffold CLI + doctor stub + pytest | concluída |
| [1](sprints/sprint-1-leitor-grafo.md) | Leitor do grafo UA | 3–4 dias | Parser + queries sobre knowledge-graph.json | concluída |
| [2](sprints/sprint-2-cliente-engram.md) | Cliente Engram | 3–4 dias | HTTP/CLI + payload mem_save | concluída |
| [3](sprints/sprint-3-sync.md) | Sync | 4–5 dias | `sync` full + incremental | concluída |
| [4](sprints/sprint-4-enrich.md) | Enrich | 3–4 dias | `enrich` + `suggest` | concluída |
| [5](sprints/sprint-5-mcp-skill.md) | MCP + Skill + Hooks | 4–5 dias | MCP server + skill Cursor | concluída |
| [6](sprints/sprint-6-release.md) | Release v1.0 | 3–4 dias | CI, docs, catálogo, tag | concluída — v1.0.0 |

**Total v1.0:** ~22–28 dias úteis

### v1.x (planejadas)

| Sprint | Nome | Duração | Entrega principal | Versão | Status |
|--------|------|---------|-------------------|--------|--------|
| [7](sprints/sprint-7-operacionalizacao-ua.md) | Operacionalização UA | 3–5 dias | Workflows, smoke, métricas sync | v1.0.1 | pendente |
| [8](sprints/sprint-8-adapter-lat-md.md) | Adapter lat.md | 2–3 sem | `sources/` + `graph import lat-md` | v1.1.0 | pendente |
| [9](sprints/sprint-9-catalogo-watchlist.md) | Catálogo + watchlist | 1–2 dias | lat.md/Potpie no catálogo; research/ | v1.1.1 | pendente |
| [10](sprints/sprint-10-research-adapters.md) | Research + adapters | 1–2 sem | Spikes Orbit/Potpie; ADRs; v1.2 | v1.2.0 | pendente |

**Total v1.x estimado:** ~5–8 semanas

Ver [PLANO-SPRINTS.md](PLANO-SPRINTS.md) para cronograma, dependências, quatro passos do roadmap e riscos.

---

## Como executar cada sprint

1. Criar branch `sprint-N/nome-curto`
2. Implementar tarefas na ordem do arquivo da sprint
3. Rodar `pytest` + `context-bridge doctor`
4. Atualizar `CHANGELOG.md` e marcar critérios de aceite
5. Merge → `master`
6. Demo: sync em projeto com grafo UA real

### Kickoff (próxima sprint — Sprint 7)

```powershell
cd context-bridge
git checkout -b sprint-7/operacionalizacao-ua
python -m pip install -e ".[dev,mcp]"
pytest -m "not network"
context-bridge doctor
# Ver tarefas: docs/sprints/sprint-7-operacionalizacao-ua.md
```

---

## Tipos de memória Engram (convenção)

| type | Origem no grafo UA | Exemplo |
|------|-------------------|---------|
| `architecture` | Camadas (API, Service, Data…) | "Layer API: 42 nodes across auth, billing" |
| `domain` | `/understand-domain` | "Payment flow: checkout → gateway → ledger" |
| `codebase-map` | Nós hub (alto grau) | "Entry point: src/api/router.ts" |
| `decision` | Manual / hook pós-chat | "Chose JWT over sessions — see auth/" |

Campo `where` sempre referencia path ou node ID do grafo UA.

---

## Definition of Done (v1.x)

### v1.0.1 — Sprint 7

- [ ] Workflows `sync-after-understand` e `enrich-before-task` publicados
- [ ] `scripts/smoke.ps1` inclui `enrich`
- [ ] Relatório sync com métricas por mapper

### v1.1.0 — Sprint 8

- [ ] `graph import lat-md` gera JSON compatível com `validate_graph()`
- [ ] `sync` / `enrich` funcionam com fonte lat-md
- [ ] `docs/SOURCES.md` documenta multi-fonte

### v1.1.1 — Sprint 9

- [ ] Catálogo lat.md e Potpie em `manifests/projects.json`
- [ ] `docs/research/watchlist.md` ativo

### v1.2.0 — Sprint 10

- [ ] Spikes Orbit KG e Potpie documentados
- [ ] ADRs 004/005 com decisão adopt/defer/reject
- [ ] Se adopt: ≥1 adapter em `sources/` com testes offline

---

## Fora de escopo

**Permanente:**

- Rodar pipeline `/understand` (responsabilidade do UA ou lat CLI)
- Substituir dashboard interativo do UA
- Sync bidirecional Engram → grafo

**Backlog pós-v1.2** (ver [PLANO-SPRINTS.md](PLANO-SPRINTS.md#backlog-pós-v12)):

- Merge UA + lat no mesmo grafo (v1.3)
- Suporte wikis Karpathy (`/understand-knowledge`)
- `context-bridge watch` — file watcher
- Plugin nativo Engram (upstream)
