# Sprint 7 — Operacionalização UA (Passo 1)

**Versão alvo:** v1.0.1  
**Duração:** 3–5 dias  
**Branch sugerida:** `sprint-7/operacionalizacao-ua`  
**Depende de:** Sprint 6 (v1.0.0 entregue)  
**Desbloqueia:** Sprint 8 (adapter lat.md)

---

## Meta

Consolidar o **Understand Anything como fonte primária** do Context Bridge: workflow canônico `doctor → sync --incremental → enrich` documentado, testável e integrado a agents — sem alterar o contrato do grafo UA.

**Passo do roadmap:** [Passo 1 — Curto prazo](../PLANO-SPRINTS.md#passo-1--curto-prazo-consolidar-ua-como-fonte-primária)

---

## Contexto

v1.0.0 entrega CLI, sync, enrich, MCP e skill. Esta sprint fecha lacunas operacionais:

- Workflows referenciados no CHANGELOG ainda não existem em `workflows/`
- `scripts/smoke.ps1` não cobre `enrich`
- Relatório de `sync` não expõe métricas por mapper
- Hooks pós-sync podem orientar melhor o próximo passo do agent

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S7.1 | Workflow pós-`/understand` — doctor → sync incremental | `workflows/sync-after-understand.md` |
| S7.2 | Workflow pré-tarefa — enrich com query e hops | `workflows/enrich-before-task.md` |
| S7.3 | Estender smoke test com `enrich` (fixture ou projeto com grafo) | `scripts/smoke.ps1` |
| S7.4 | Skill: referenciar workflows e critérios WARN vs FAIL | `skill/SKILL.md` |
| S7.5 | Hook pós-sync: sugerir query template para `enrich` | `context_bridge/hooks/post_sync.py` |
| S7.6 | Métricas no relatório sync: idade do grafo, contagem por mapper, duração | `context_bridge/sync/report.py` |
| S7.7 | README: seção "Workflow recomendado" linkando workflows | `README.md` |
| S7.8 | ARCHITECTURE: fluxo operacional pós-v1.0 | `docs/ARCHITECTURE.md` |
| S7.9 | Testes: relatório sync com métricas; smoke script invocável em CI (opcional) | `tests/test_sync_report.py` |
| S7.10 | Bump versão `1.0.1` | `pyproject.toml`, `CHANGELOG.md` |

---

## Workflow canônico (referência)

| Fase | Comando / MCP | Quando | Side effects |
|------|---------------|--------|--------------|
| Pré-flight | `doctor` / `bridge_doctor` | Antes de sync | Nenhum |
| Pós-`/understand` | `sync --incremental` | Grafo novo/atualizado | Upsert Engram |
| Pré-tarefa | `enrich "<query>"` | Antes de editar módulo | Nenhum |
| Preview | `suggest` | Debug / onboarding | Nenhum |

**Regra:** Context Bridge **nunca** executa `/understand`.

---

## Critérios de aceite

- [x] `workflows/sync-after-understand.md` e `workflows/enrich-before-task.md` existem e estão linkados no README
- [x] `scripts/smoke.ps1` inclui `enrich` e exit 0 com fixture de teste
- [x] `sync --incremental` no mesmo grafo → 100% skipped (hash inalterado) — coberto por `tests/test_sync_engine.py::test_run_sync_second_run_skips_unchanged`
- [x] Relatório sync lista contagem por tipo (`architecture`, `domain`, `codebase-map`, `tour`)
- [x] `skill/SKILL.md` aponta para os dois workflows
- [x] `pytest -m "not network"` verde
- [x] CHANGELOG v1.0.1 publicado

---

## Comandos de validação

```powershell
pytest -m "not network"
.\scripts\smoke.ps1
context-bridge doctor
context-bridge sync --dry-run --incremental --verbose
context-bridge enrich "authentication flow" --json --limit 5
```

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Smoke `enrich` falha sem Engram | Usar `--project` apontando para fixture; enrich degrada sem backend |
| Doc drift entre skill e workflows | Um workflow = uma fonte; README só linka |

---

## Demo ao fechar sprint

1. Projeto com grafo UA (fixture ou real)
2. `context-bridge doctor` → OK/WARN esperados
3. `sync --incremental` → relatório com métricas por mapper
4. `enrich "auth"` → JSON com memories + graph_nodes
5. Agent segue `workflows/sync-after-understand.md` end-to-end
