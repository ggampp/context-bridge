# ADR-005 — Adapter Potpie context graph

**Status:** defer
**Data:** 2026-07-01
**Decisores:** Sprint 10 (research spikes)

---

## Contexto

[Potpie](https://github.com/potpie-ai/potpie) mantém living context graph local (daemon + `potpie ui`) para coding agents. Parcialmente dependente de conta Potpie para features gerenciadas.

Spike técnico real (tentativa de instalação nativa Windows + WSL2 Ubuntu, pesquisa documental do README e `docs/context-graph/architecture.md`): ver [`docs/research/potpie-spike.md`](../research/potpie-spike.md).

## Decisão

**Defer.**

2 de 5 no checklist go/no-go — abaixo do limiar de go (≥4):

- ✅ Self-hosted sem cloud obrigatória para uso básico
- ✅ Licença permissiva (Apache-2.0)
- ⚠️ Export JSON ("Snapshot") mencionado na doc, mas sem schema público
  documentado nem verificável (setup não completou neste spike)
- ⚠️ Modelo de dados é uma **ontologia customizável por projeto**
  (`domain/ontology.py`), não um schema fixo de nós/arestas simples —
  mapeamento para `GraphNode`/`GraphEdge` exigiria entender/normalizar essa
  ontologia primeiro, não apenas ler um export
- ❌ Esforço claramente maior que o adapter lat.md: pacote ainda em **beta**
  (v2.0.0b3), árvore de dependências pesada (~200MB incluindo torch/
  transformers/scipy só para a CLI), exige Python ≥3.12, e o backend padrão
  (`FalkorDBLite`) **quebra em instalação nativa no Windows** — depende de
  `redislite`, que não suporta `win32` (confirmado via erro real de build:
  `The redislite module is not supported on the 'win32' platform`) — apesar
  da própria documentação de arquitetura afirmar que o sistema "evita Redis
  explicitamente", indicando que a doc está à frente do que o release beta
  realmente empacota.

## Consequências

- Nenhum adapter `sources/potpie.py` implementado nesta versão (v1.2.0).
- Instalação funcional só é viável em Linux/WSL nesta versão do Potpie —
  relevante caso o projeto seja revisitado, já que Context Bridge roda em
  Windows/macOS/Linux.
- `docs/research/watchlist.md` atualizada com o achado e nova data de
  reavaliação.
- Reavaliar quando: (a) uma versão estável (não-beta) for publicada, (b) o
  export "Snapshot" JSON estiver documentado com schema público estável, e
  (c) o footprint de dependências for reduzido ou o backend padrão suportar
  Windows nativamente.
