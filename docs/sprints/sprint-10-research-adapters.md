# Sprint 10 — Research spikes e adapters v1.2 (Passo 3)

**Versão alvo:** v1.2.0 (se go/no-go = go para ≥1 adapter) ou v1.2.0-docs (só ADRs defer)  
**Duração:** 1–2 semanas  
**Branch sugerida:** `sprint-10/research-adapters`  
**Depende de:** Sprint 8 (camada `sources/`), Sprint 9 (watchlist)  
**Desbloqueia:** backlog v1.3 (merge UA+lat, watch contínuo)

---

## Meta

Executar **spikes técnicos** em GitLab Orbit KG e Potpie; decidir via ADR se implementa adapter em `sources/`. Manter monitoramento contínuo documentado.

**Passo do roadmap:** [Passo 3 — Pesquisa contínua](../PLANO-SPRINTS.md#passo-3--pesquisa-contínua-orbit-kg--potpie)

---

## Fase A — Monitoramento (contínuo, inicia na Sprint 9)

| Atividade | Cadência | Ferramenta |
|-----------|----------|------------|
| Atualizar watchlist | Quinzenal | `docs/research/watchlist.md` |
| Snapshot Potpie | Mensal | `agent-reach-tech research oss potpie --repo potpie-ai/potpie` |
| Checar Orbit KG | Mensal | docs GitLab + `agent-reach-tech web` |

Script opcional: `scripts/watch-research.ps1` → grava em `docs/research/snapshots/`.

---

## Fase B — Spike Orbit KG (1 semana, WSL/Linux recomendado)

```bash
# Inventário — não commitar dados de repos privados
curl -fsSL https://gitlab.com/gitlab-org/rust/knowledge-graph/-/raw/main/install.sh | bash
cd $PROJECT && gkg index
gkg server start
# Documentar: formato on-disk, respostas MCP, amostra anonimizada
```

| Entregável | Arquivo |
|------------|---------|
| Relatório spike | `docs/research/orbit-kg-spike.md` |
| Fixture anonimizada | `tests/fixtures/orbit_sample.json` (se exportável) |
| Stub adapter | `context_bridge/sources/orbit_kg.py` (se go) |
| ADR | `docs/adr/004-orbit-kg-adapter.md` |

---

## Fase C — Spike Potpie (1 semana)

```powershell
uv tool install potpie
potpie setup
# Indexar repo de teste; localizar storage do daemon (~/.potpie ou config)
potpie ui
```

| Entregável | Arquivo |
|------------|---------|
| Relatório spike | `docs/research/potpie-spike.md` |
| ADR | `docs/adr/005-potpie-adapter.md` |

---

## Checklist go/no-go (copiar de `go-no-go-adapters.md`)

| # | Pergunta | Go se… |
|---|----------|--------|
| 1 | Export JSON/API estável? | Documentado + fixture |
| 2 | Nós com `path` e relações tipadas? | Mapeável para `GraphNode` |
| 3 | Self-hosted sem cloud obrigatória? | Sim ou degradação aceitável |
| 4 | Licença compatível MIT? | Sim |
| 5 | Esforço ≤ adapter lat.md? | Estimativa ≤ 2 semanas |

**Go:** ≥4 favoráveis → implementar `sources/<nome>.py` + testes.  
**No-go:** ADR `defer` com data de reavaliação.

---

## Entregáveis Sprint 10

| ID | Tarefa | Condição |
|----|--------|----------|
| S10.1 | Spike Orbit KG documentado | Obrigatório — feito (instalação real via WSL2, gkg 0.25.0) |
| S10.2 | Spike Potpie documentado | Obrigatório — feito (instalação real: falha nativa Windows + tentativas WSL2, complementado com pesquisa documental) |
| S10.3 | ADR-004 e ADR-005 | Obrigatório — feito, ambos **defer** |
| S10.4 | Adapter `orbit_kg.py` ou `potpie.py` | Se go — **não aplicável** (nenhum atingiu ≥4/5) |
| S10.5 | Testes offline do adapter | Se go — não aplicável |
| S10.6 | `graph-source.yaml` estendido | Se go — não aplicável |
| S10.7 | `scripts/watch-research.ps1` | Opcional — não implementado nesta sprint (backlog) |
| S10.8 | Bump `1.2.0` + CHANGELOG | Ao fechar — feito |

---

## Critérios de aceite

- [x] Dois relatórios de spike em `docs/research/` (`orbit-kg-spike.md`, `potpie-spike.md`)
- [x] Dois ADRs com decisão explícita: **adopt / defer / reject** (ADR-004 e ADR-005 → **defer** ambos)
- [x] Watchlist atualizada com findings dos spikes
- [x] Se adapter implementado: `graph import <source>` + `sync --dry-run` verde — N/A (nenhum adapter: ambos os spikes resultaram em defer, 2/5 no checklist go/no-go)
- [x] `pytest -m "not network"` verde (180 testes, inalterado — nenhum código novo nesta sprint)

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Orbit repo privado / 404 | Spike só com GKG público + docs Orbit |
| Potpie exige login cloud | ADR defer; watchlist continua |
| Scope creep v1.2 | Máximo 1 adapter por release |

---

## Demo ao fechar sprint

1. Apresentar ADRs em `docs/adr/`
2. Se adapter: demo `graph import` + sync dry-run
3. Atualizar watchlist com próxima data de revisão
