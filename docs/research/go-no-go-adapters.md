# Go/no-go — novos adapters de grafo

Checklist para decidir se um projeto candidato entra no Context Bridge como fonte em `sources/`.  
Usado na [Sprint 10](sprints/sprint-10-research-adapters.md).

---

## Perguntas

| # | Pergunta | Go se… | Orbit KG (gkg 0.25.0) | Potpie (2.0.0b3) |
|---|----------|--------|----------|--------|
| 1 | Existe export JSON ou API local estável? | Documentado + amostra reproduzível | ❌ Parquet interno sem schema público; MCP retorna texto p/ LLM, não JSON de grafo | ⚠️ "Snapshot" JSON mencionado, sem schema documentado nem verificado |
| 2 | Nós têm `path` e relações tipadas (`imports`, `calls`, …)? | Mapeável para `GraphNode` / `GraphEdge` | ✅ `FileNode`/`DefinitionNode` com `path`; relações tipadas | ⚠️ Ontologia customizável por projeto, não schema fixo |
| 3 | Self-hosted sem conta cloud obrigatória? | Sim, ou degradação aceitável documentada | ✅ Sim, 100% local | ✅ Sim, para uso básico (`potpie login` é opcional) |
| 4 | Licença compatível com Context Bridge (MIT)? | Sim | ✅ MIT | ✅ Apache-2.0 (permissiva) |
| 5 | Esforço de implementação ≤ adapter lat.md (~2–3 sem)? | Estimativa aprovada | ❌ Exigiria depender de formato não documentado (Parquet) ou scraping de texto MCP | ❌ Beta imaturo, ~200MB de deps, quebra no Windows nativo, exige Python ≥3.12 |
| | **Total favorável** | | **2/5** | **2/5** |

---

## Regra de decisão

| Resultado | Ação |
|-----------|------|
| ≥4 respostas favoráveis | **adopt** — implementar `sources/<nome>.py` + testes + ADR |
| 2–3 favoráveis | **defer** — manter na watchlist; reavaliar em 30–60 dias |
| ≤1 favorável | **reject** — ADR com motivo; não implementar |

---

## ADRs

| ADR | Projeto | Decisão | Data |
|-----|---------|---------|------|
| [004](../adr/004-orbit-kg-adapter.md) | GitLab Orbit KG (gkg) | **defer** | 2026-07-01 |
| [005](../adr/005-potpie-adapter.md) | Potpie | **defer** | 2026-07-01 |

---

## Referências

- [Watchlist](watchlist.md)
- [Sprint 8 — lat.md](../sprints/sprint-8-adapter-lat-md.md)
- Pesquisa inicial: agent-reach-tech discover "codebase knowledge graph" (2026-06-30)
