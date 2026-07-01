# Sprint 4 — Enrich & Suggest

**Duração:** 3–4 dias  
**Branch sugerida:** `sprint-4/enrich`  
**Depende de:** Sprint 1, Sprint 2, Sprint 3 (recomendado)  
**Desbloqueia:** Sprint 5

---

## Meta

Implementar busca híbrida: memórias Engram enriquecidas com nós e relações do grafo UA, plus comando `suggest` para agents.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S4.1 | Parser campo `where` — extrair paths e node IDs de memórias | `context_bridge/enrich/where_parser.py` |
| S4.2 | Resolver path → nós do grafo + vizinhos (1 hop) | `context_bridge/enrich/graph_context.py` |
| S4.3 | Pipeline enrich: query → Engram search → attach graph context | `context_bridge/enrich/pipeline.py` |
| S4.4 | Formato output markdown (agent-friendly) | `context_bridge/enrich/format_md.py` |
| S4.5 | Formato output JSON (`--json`) | `context_bridge/enrich/format_json.py` |
| S4.6 | CLI `enrich QUERY` — flags: `--json`, `--hops N`, `--limit N` | `context_bridge/cli.py` |
| S4.7 | `suggest` — gera payloads mem_save do grafo sem gravar (subset do sync) | `context_bridge/suggest.py` |
| S4.8 | CLI `suggest` — flags: `--types`, `--json` | `context_bridge/cli.py` |
| S4.9 | Hook template pós-research style — bloco Engram opcional no output | `context_bridge/hooks/post_sync.py` |
| S4.10 | Testes pipeline com memórias + grafo fixture | `tests/test_enrich_pipeline.py` |
| S4.11 | Testes where_parser edge cases | `tests/test_enrich_where.py` |
| S4.12 | Testes suggest output schema | `tests/test_suggest.py` |

---

## Exemplo output enrich (markdown)

```markdown
## Enrich: "auth flow"

### Memórias Engram (2)
1. **Architecture layer: API** — 42 nodes...
   - Graph: `src/api/router.ts` → calls `src/auth/login.ts`, `src/auth/middleware.ts`

### Contexto do grafo (relacionado)
| Nó | Camada | Resumo |
|----|--------|--------|
| src/auth/login.ts | api | Handles user login... |
| src/auth/middleware.ts | api | JWT validation... |
```

---

## Critérios de aceite

- [ ] `context-bridge enrich "auth"` retorna memórias + nós relacionados
- [ ] `--json` produz schema estável documentado
- [ ] `context-bridge suggest --json` retorna lista de payloads válidos
- [ ] Memórias sem `where` ainda aparecem; graph context omitido gracefully
- [ ] `pytest tests/test_enrich*` passa offline

---

## Comandos de validação

```powershell
context-bridge sync --dry-run
context-bridge enrich "architecture" --json
context-bridge suggest --types architecture,hubs --json
pytest tests/test_enrich_pipeline.py
```

---

## Notas técnicas

- Default `--hops 1` — evitar explosão combinatória em grafos densos
- `--limit 10` memórias Engram + `--limit 15` nós grafo
- `suggest` reutiliza mappers da Sprint 3 sem side effects
- Formato JSON versionado: `{ "version": 1, "query": "...", "memories": [...], "graph_nodes": [...] }`

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Enrich lento em grafo grande | Index path→node na Sprint 1; cache session |
| Falsos positivos path match | Match exato primeiro, prefix depois |

---

## Demo ao fechar sprint

Perguntar ao agent (ou CLI): `context-bridge enrich "payment flow"` após sync em projeto com domínios UA.
