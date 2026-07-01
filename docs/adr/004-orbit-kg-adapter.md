# ADR-004 — Adapter GitLab Orbit Knowledge Graph

**Status:** defer
**Data:** 2026-07-01
**Decisores:** Sprint 10 (research spikes)

---

## Contexto

GitLab Knowledge Graph (`gkg`) indexa repositórios em grafo queryable com MCP. Projeto legado em maintenance; sucessor [Orbit KG](https://gitlab.com/gitlab-org/orbit/knowledge-graph) em desenvolvimento.

Spike técnico real (instalação + indexação + servidor MCP, não simulado): ver [`docs/research/orbit-kg-spike.md`](../research/orbit-kg-spike.md).

## Decisão

**Defer.**

`gkg` (a ferramenta atual, testável hoje) não atinge o limiar de go
(≥4/5 no checklist) — 2 de 5 favoráveis:

- ✅ Nós com `path` e relações tipadas
- ✅ Self-hosted sem cloud
- ✅ Licença MIT
- ❌ Sem export JSON/API estável documentado (Parquet interno sem schema
  público garantido; MCP retorna texto formatado para LLM, não grafo bruto)
- ❌ Esforço de adapter > lat.md (exigiria depender de formato não
  documentado, ou fazer parsing frágil da saída MCP orientada a prompt)

Além disso, `gkg` está oficialmente em **modo manutenção** — o sucessor
"Orbit KG" (`gitlab-org/orbit/knowledge-graph`) é um projeto diferente e,
no momento deste spike, não foi encontrado publicamente acessível para
teste (provavelmente ainda interno). Não há como avaliar o sucessor
tecnicamente até que seja publicado.

## Consequências

- Nenhum adapter `sources/orbit_kg.py` ou `sources/gkg.py` implementado
  nesta versão (v1.2.0).
- `docs/research/watchlist.md` atualizada com o achado e nova data de
  reavaliação.
- Reavaliar quando: (a) o sucessor Orbit KG for publicado, ou (b) `gkg`
  documentar formalmente um export JSON estável (o dado técnico necessário
  já existe — grafo tipado com paths — falta apenas uma interface pública
  garantida para consumir sem depender de scraping do Parquet interno ou
  do texto MCP).
- Diferente do lat.md (ADR-003), aqui o risco não é falta de dados
  estruturados — é falta de um **contrato público estável** para consumi-los.
