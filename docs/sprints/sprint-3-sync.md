# Sprint 3 — Sync (Grafo → Engram)

**Duração:** 4–5 dias  
**Branch sugerida:** `sprint-3/sync`  
**Depende de:** Sprint 1, Sprint 2  
**Desbloqueia:** Sprint 4, Sprint 5

---

## Meta

Implementar `context-bridge sync` — converte partes relevantes do grafo UA em memórias Engram, com modo full e incremental.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S3.1 | `config/sync-rules.yaml` — regras default (layers, hubs, domains) | `config/sync-rules.yaml` |
| S3.2 | Loader de regras YAML | `context_bridge/sync/rules.py` |
| S3.3 | Mapper: camadas arquiteturais → memórias `architecture` | `context_bridge/sync/mappers/layers.py` |
| S3.4 | Mapper: nós hub → memórias `codebase-map` | `context_bridge/sync/mappers/hubs.py` |
| S3.5 | Mapper: domínios → memórias `domain` (se dados presentes) | `context_bridge/sync/mappers/domains.py` |
| S3.6 | Mapper: guided tours → memória `architecture` resumo | `context_bridge/sync/mappers/tours.py` |
| S3.7 | Orquestrador sync — aplica mappers, dedup, batch save | `context_bridge/sync/engine.py` |
| S3.8 | Estado incremental — `.context-bridge/sync-state.json` (hash grafo, obs_ids) | `context_bridge/sync/state.py` |
| S3.9 | Modo incremental — só nós alterados (via diff overlay ou fingerprint) | `context_bridge/sync/incremental.py` |
| S3.10 | CLI `sync` — flags: `--dry-run`, `--incremental`, `--force`, `--project PATH` | `context_bridge/cli.py` |
| S3.11 | Output relatório sync — created / updated / skipped / errors | `context_bridge/sync/report.py` |
| S3.12 | Testes engine com grafo fixture + Engram mock | `tests/test_sync_engine.py` |
| S3.13 | Testes incremental — segundo sync não duplica | `tests/test_sync_incremental.py` |
| S3.14 | E2E offline — dry-run produz N payloads esperados | `tests/test_sync_e2e.py` |

---

## Regras default (`sync-rules.yaml`)

```yaml
version: 1
layers:
  enabled: true
  min_nodes: 3          # ignora camadas triviais
hubs:
  enabled: true
  min_degree: 5
  max_nodes: 20         # top N hubs
domains:
  enabled: true
tours:
  enabled: true
  max_tours: 3
project_tag: context-bridge
topic_key_prefix: cb-
```

---

## Fluxo sync

```
knowledge-graph.json
    → validate
    → apply mappers (rules)
    → build mem_save payloads
    → dedup by topic_key
    → EngramClient.save / update
    → write sync-state.json
    → print report
```

---

## Critérios de aceite

- [ ] `context-bridge sync --dry-run` lista payloads sem gravar
- [ ] `context-bridge sync` grava memórias no Engram (manual ou mock)
- [ ] Segundo `sync --incremental` atualiza só o que mudou
- [ ] `--force` reprocessa tudo ignorando state
- [ ] Relatório mostra contadores claros
- [ ] `pytest tests/test_sync*` passa offline

---

## Comandos de validação

```powershell
context-bridge sync --dry-run --project .
context-bridge sync --incremental --project .
context-bridge sync --force --project .
pytest tests/test_sync_engine.py -v
```

---

## Notas técnicas

- Não sincronizar **todos** os nós — só agregados úteis (camadas, hubs, domínios)
- Limite de tamanho `what` field: 500 chars (compatível Engram / agent-reach-tech)
- `sync-state.json` deve ir no `.gitignore` do projeto alvo (local state)
- Opcional: `--types architecture,domain` para filtrar mappers

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Centenas de memórias | Caps em hubs/tours; regras configuráveis |
| Grafo stale | doctor WARN + sync report "graph age: N days" |

---

## Demo ao fechar sprint

```powershell
context-bridge sync --dry-run
context-bridge sync
engram search "architecture layer"
```

Mostrar memórias criadas com prefixo `cb-` no Engram TUI ou search.
