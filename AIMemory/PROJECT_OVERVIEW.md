# Visão Geral do Projeto

> Ponte thin entre Understand Anything (grafo estrutural) e Engram (memória persistente).
> Leia após `INDEX.md` e antes do tail de `work.log`.

## O que é este projeto

**context-bridge** lê o grafo de conhecimento (UA ou lat.md, via `sources/`), mapeia camadas/domínios/hubs para payloads `mem_save`, sincroniza incrementalmente com Engram (HTTP `engram serve` ou CLI), e oferece busca híbrida `enrich` (memória + nós do grafo). CLI + MCP (4 tools) + skill. **v1.2.0 entregue — todas as sprints planejadas (0–10) concluídas.**

## Build / test / lint

```powershell
cd context-bridge
pip install -e ".[dev,mcp]"
pytest -m "not network"
context-bridge doctor
.\scripts\smoke.ps1
```

## Convenções

- Pacote: `context_bridge` · CLI: `context-bridge`
- Grafo UA: nós (`id`, `path`, `layer`, `domain`, `summary`) + edges tipadas
- Sync: `topic_key` prefix `cb-` · estado em `.context-bridge/sync-state.json` (gitignored)
- Mappers: `sync/mappers/` driven by `config/sync-rules.yaml`
- Enrich: parser `**Where**:` com anchors `#layer:`, `#node:`, `#domain:`, `#tours:`
- Memórias Engram: tipos `architecture`, `domain`, `codebase-map`, `decision`

## Regras rígidas

- **Nunca** executar `/understand` — responsabilidade do UA
- **Nunca** escrever em `.understand-anything/*.json`
- **Nunca** substituir servidor MCP nativo do Engram
- Sync idempotente — usar `--incremental` após cada `/understand`
- Testes default offline; `@network` só com Engram real rodando

## Armadilhas conhecidas

- Sem Engram: `doctor` WARN, `sync` falha gravar, `enrich` sem memórias úteis — degradação esperada
- Sem grafo UA nem lat.md: `sync`/`suggest` precisam de uma fonte disponível; `enrich` retorna só memórias sem contexto de grafo
- Nós lat.md não populam `layer` — mapper `architecture` os agrupa sob `"unknown"`; desabilitar via `sync-rules.yaml: layers.enabled: false` se necessário (backlog v1.1.1: `layer:` via frontmatter)
- Fontes de grafo (`ua`, `lat-md`) não são mescladas — a primeira disponível em `config/graph-source.yaml: priority` vence integralmente (merge é backlog v1.3)

## Decisões travadas

- Thin bridge, Engram-first, referência não cópia (DESENVOLVIMENTO.md)
- UA fonte primária; lat.md segunda fonte via `sources/`, adotada v1.1.0 (Sprint 8)
- Orbit KG (`gkg`) e Potpie: **defer** após spike real (Sprint 10, ADR-004/005) — nenhum adapter implementado, ambos 2/5 no checklist go/no-go

## Trabalho recente

- **v1.0.0** — sprints 0–6 completas, 118+ testes offline
- **v1.0.1** — Sprint 7: workflows canônicos, smoke `enrich`, métricas de sync
- **v1.1.0** — Sprint 8: camada `sources/` conectada (CLI `graph import lat-md`,
  `graph_ref` configurável, doctor detecta `lat.md/`), 180 testes offline
- **v1.1.1** — Sprint 9: catálogo lat.md/Potpie, links cruzados, watchlist validada
- **v1.2.0** — Sprint 10: spikes reais Orbit KG (gkg) e Potpie (instalação de
  verdade em WSL2 + Windows nativo) — ambos **defer**, nenhum adapter novo

## Próximo trabalho

Nenhuma sprint planejada pendente (0–10 concluídas). Backlog pós-v1.2 em
`docs/PLANO-SPRINTS.md`: merge UA+lat (v1.3), `scripts/watch-research.ps1`
(monitoramento contínuo, opcional), reavaliar Orbit KG/Potpie conforme
critérios de reavaliação nos ADRs 004/005.

## Onde olhar

| Necessidade | Caminho |
|-------------|---------|
| Roadmap | `docs/PLANO-SPRINTS.md` |
| Arquitetura | `docs/ARCHITECTURE.md` |
| Fontes de grafo | `docs/SOURCES.md` |
| Spikes research | `docs/research/orbit-kg-spike.md`, `potpie-spike.md` |
| Watchlist adapters | `docs/research/watchlist.md` |
| Skill / MCP | `skill/SKILL.md`, `docs/MCP-SETUP.md` |

---
Última atualização: 2026-07-01
