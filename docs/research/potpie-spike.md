# Spike — Potpie

**Data:** 2026-07-01
**Ambiente:** Windows (nativo) + WSL2 Ubuntu — instalação real tentada, não simulada
**Versão testada:** `potpie` 2.0.0b3 (beta, via PyPI)

---

## O que foi feito

1. **Instalação nativa Windows** (`uv tool install potpie`): **falhou**. Build da
   dependência transitiva `falkordblite==0.10.0` (via `potpie-context-engine`)
   quebra explicitamente:
   ```
   The redislite module is not supported on the 'win32' platform
   ```
   `falkordblite` é o backend de grafo local padrão do Potpie (FalkorDB embutido,
   baseado em `redislite`) — sem suporte nativo a Windows.
2. **Instalação via WSL2 Ubuntu** (ambiente recomendado pelo próprio Sprint 10):
   três tentativas de `uv tool install potpie` (~140 pacotes, incluindo
   `torch` 108MB, `scipy` 35MB, `transformers` 10MB, `scikit-learn`, `numpy`,
   `grpcio`, `pillow` — footprint pesado para uma CLI). Todas as três tentativas
   foram interrompidas antes de completar o download, independente da estratégia
   (pipe direto, redirecionamento a arquivo, `nohup`+`disown` totalmente
   desacoplado) — limitação de execução em background de downloads longos
   neste ambiente sandboxed, não um erro do próprio Potpie. Não foi possível
   completar `potpie setup` / `potpie ui` ao vivo dentro da janela disponível
   deste spike.
3. Complementado com pesquisa documental (README + `docs/context-graph/architecture.md`
   do repositório oficial) para responder ao checklist com o que pôde ser
   confirmado sem execução ao vivo.

## Achados (documentação oficial)

- **Arquitetura do grafo:** modelo **orientado a ontologia** — entidades,
  relações, "claims" e eventos definidos em `domain/ontology.py`, não um
  schema fixo de nós/arestas pronto para consumo. Cada projeto define/ajusta
  sua própria ontologia; não há um `GraphNode`/`GraphEdge` universal simples
  como no lat.md ou no `gkg`.
- **Backend padrão:** `FalkorDBLite` — "OSS default on Python ≥3.12: embedded
  FalkorDBLite local graph with vector search". Requer **Python ≥3.12**.
  Perfis alternativos: Neo4j, PostgreSQL/pgvector, Chroma, embedded JSON
  (fallback sem Docker), in-memory (testes).
- **Discrepância doc vs. pacote real:** a documentação da arquitetura diz que
  o sistema "evita Redis explicitamente" e usa pgvector/vetores embutidos —
  mas o pacote beta publicado (`potpie-context-engine 0.1.0b3`) **ainda
  depende de `falkordblite`, que por sua vez depende de `redislite`** — daí
  a quebra real observada no Windows. A arquitetura documentada parece estar
  à frente do que o release beta atual efetivamente empacota.
- **Export:** existe menção a "Portable pot export/import" (Snapshot) em
  formato JSON — mas sem schema publicamente documentado nem testável neste
  spike (setup não completou).
- **Cloud/conta:** operação **híbrida** — setup local provisiona config,
  storage, daemon e "agent skills" sem conta; `potpie login` habilita
  "features gerenciadas" (opcional, não bloqueante para uso local básico).
- **Licença:** Apache-2.0 (confirmado no README).

## Checklist go/no-go

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Export JSON/API estável? | **Parcial** — "Snapshot" JSON mencionado, sem schema público documentado nem verificado ao vivo |
| 2 | Nós com `path` e relações tipadas mapeáveis? | **Não confirmado** — modelo é uma ontologia customizável por projeto (`domain/ontology.py`), não um schema fixo simples |
| 3 | Self-hosted sem cloud obrigatória? | **Sim** — core local funciona sem `potpie login`; features gerenciadas são opcionais |
| 4 | Licença compatível? | **Sim** — Apache-2.0 (permissiva) |
| 5 | Esforço ≤ adapter lat.md (~2–3 sem)? | **Não** — pacote beta (v2.0.0b3), árvore de dependências pesada (~200MB incl. torch/transformers/scipy) só para a CLI, requer Python ≥3.12, backend padrão quebra no Windows nativo, modelo de dados é ontologia customizável (não um schema fixo pronto) |

**Resultado: 2 de 5 favoráveis → não atinge o limiar de "go" (≥4).**

## Decisão

**Defer.** Ver [ADR-005](../adr/005-potpie-adapter.md). Diferente do Orbit KG
(onde o bloqueio é falta de export público estável sobre dados já bons), o
bloqueio do Potpie é uma combinação de: (a) imaturidade do release beta,
(b) footprint de dependências pesado para uma CLI, (c) incompatibilidade
nativa com Windows no backend padrão, e (d) modelo de dados customizável por
ontologia em vez de um schema fixo simples de mapear. Reavaliar quando uma
versão estável (não-beta) for publicada e o Snapshot/export JSON estiver
documentado com schema público.
