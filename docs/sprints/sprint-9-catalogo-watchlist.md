# Sprint 9 — Catálogo e watchlist (Passo 4 + início Passo 3)

**Versão alvo:** v1.1.1 (docs/catálogo; sem bump funcional obrigatório)  
**Duração:** 1–2 dias (pode correr **em paralelo** com Sprint 8)  
**Branch sugerida:** `sprint-9/catalogo-watchlist`  
**Depende de:** Sprint 6 (v1.0.0) — independente de Sprint 8  
**Desbloqueia:** Sprint 10 (watchlist alimenta spikes)

---

## Meta

Documentar **lat.md** e **Potpie** no catálogo do repositório pai e iniciar a **gestão de evolução** de adapters futuros via watchlist de pesquisa.

**Passos do roadmap:**

- [Passo 4 — Catálogo](../PLANO-SPRINTS.md#passo-4--catálogo-entradas-latmd-e-potpie)
- Início do [Passo 3 — Pesquisa contínua](../PLANO-SPRINTS.md#passo-3--pesquisa-contínua-orbit-kg--potpie)

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S9.1 | Entrada catálogo lat.md | `catalog/ai-agents/knowledge/lat-md.md` |
| S9.2 | Entrada catálogo Potpie | `catalog/ai-agents/knowledge/potpie.md` |
| S9.3 | Atualizar UA — link lat.md em Relacionados | `catalog/ai-agents/knowledge/understand-anything.md` |
| S9.4 | Atualizar Context Bridge — seção "Fontes de grafo" | `catalog/ai-agents/integration/context-bridge.md` |
| S9.5 | Entradas `lat-md` e `potpie` em manifests | `manifests/projects.json` |
| S9.6 | Watchlist de pesquisa (template + entradas iniciais) | `docs/research/watchlist.md` |
| S9.7 | Critério go/no-go para adapters v1.2 | `docs/research/go-no-go-adapters.md` |
| S9.8 | README pai — mapa relações atualizado (se necessário) | `../README.md` |
| S9.9 | Validar busca agent-reach-tech | `agent-reach-tech catalog search lat.md` |
| S9.10 | CHANGELOG — entrada docs v1.1.1 (opcional) | `CHANGELOG.md` |

---

## Conteúdo mínimo `watchlist.md`

| Data | Projeto | Versão/tag | Achado | Impacto adapter | Decisão |
|------|---------|------------|--------|-----------------|---------|
| 2026-06-30 | GitLab GKG | maintenance | Sucessor Orbit KG em dev | alto | observar |
| 2026-06-30 | Potpie | main | Context graph + daemon local | médio | observar |
| 2026-06-30 | lat.md | main | Adapter planejado Sprint 8 | alto | em desenvolvimento |

Cadência de revisão: **quinzenal** (registrar próxima data no arquivo).

---

## Critérios de aceite

- [x] `catalog search "lat.md"` e `"potpie"` retornam entradas
- [x] Links cruzados UA ↔ lat.md ↔ context-bridge bidirecionais
- [x] `manifests/projects.json` válido JSON com 2 novas entradas
- [x] `docs/research/watchlist.md` com ≥3 linhas iniciais (6 linhas, criadas no planejamento v1.x)
- [x] `docs/research/go-no-go-adapters.md` com checklist de 5 perguntas (criado no planejamento v1.x)

---

## Comandos de validação

```powershell
agent-reach-tech catalog search "lat.md"
agent-reach-tech catalog search "potpie"
agent-reach-tech catalog search "context bridge"
```

---

## Notas

Esta sprint **não implementa código** no pacote `context_bridge` (exceto CHANGELOG opcional). Pode ser mergeada antes ou durante Sprint 8.
