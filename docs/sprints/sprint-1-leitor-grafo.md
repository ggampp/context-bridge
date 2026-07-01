# Sprint 1 — Leitor do Grafo UA

**Duração:** 3–4 dias  
**Branch sugerida:** `sprint-1/leitor-grafo`  
**Depende de:** Sprint 0  
**Desbloqueia:** Sprint 3 (parcial), Sprint 4

---

## Meta

Ler, validar e consultar o grafo gerado pelo Understand Anything em `.understand-anything/`, com modelos tipados e queries reutilizáveis.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S1.1 | Modelos Pydantic ou dataclasses: `GraphNode`, `GraphEdge`, `KnowledgeGraph` | `context_bridge/graph/models.py` |
| S1.2 | Loader: ler `knowledge-graph.json` + `config.json` | `context_bridge/graph/loader.py` |
| S1.3 | Validador de schema — campos obrigatórios, version, referential integrity básica | `context_bridge/graph/validate.py` |
| S1.4 | Query: nós por camada arquitetural (`layer`) | `context_bridge/graph/queries.py` |
| S1.5 | Query: nós hub (grau de conexão ≥ N, default 5) | `context_bridge/graph/queries.py` |
| S1.6 | Query: nós por path de arquivo (prefix match) | `context_bridge/graph/queries.py` |
| S1.7 | Query: domínios de negócio (se presentes no JSON — domain view) | `context_bridge/graph/queries.py` |
| S1.8 | Query: diff overlay — ler `diff-overlay.json` se existir | `context_bridge/graph/diff.py` |
| S1.9 | CLI: `context-bridge graph stats` — resumo (nodes, edges, layers, languages) | `context_bridge/cli.py` |
| S1.10 | CLI: `context-bridge graph node ID\|PATH` — detalhe de um nó | `context_bridge/cli.py` |
| S1.11 | Fixtures: grafo mínimo sintético + fragmento real anonimizado | `tests/fixtures/graph_minimal.json` |
| S1.12 | Testes unitários loader, validate, queries | `tests/test_graph_*.py` |
| S1.13 | Integrar graph check no `doctor` — JSON válido, idade vs git | `context_bridge/doctor.py` |

---

## Schema UA esperado (referência)

Campos típicos em `knowledge-graph.json` (UA pode variar — tratar como best-effort):

```json
{
  "version": "...",
  "nodes": [
    {
      "id": "...",
      "label": "...",
      "type": "file|function|class|...",
      "path": "src/auth/login.ts",
      "layer": "api|service|data|...",
      "summary": "..."
    }
  ],
  "edges": [
    { "source": "...", "target": "...", "type": "imports|calls|..." }
  ]
}
```

Documentar campos suportados em comentário no loader; log WARN para campos desconhecidos.

---

## Critérios de aceite

- [ ] `context-bridge graph stats` funciona com fixture local
- [ ] `context-bridge graph node src/auth/login.ts` retorna nó ou 404 claro
- [ ] Loader falha com mensagem útil se JSON corrompido
- [ ] `doctor` reporta: grafo presente, node count, last modified
- [ ] `pytest tests/test_graph*` passa offline

---

## Comandos de validação

```powershell
context-bridge graph stats --project .
context-bridge graph node src/main.py
context-bridge doctor
pytest tests/test_graph_loader.py tests/test_graph_queries.py
```

---

## Notas técnicas

- Não carregar grafo inteiro na memória duas vezes — cache lazy por `project_root`
- Grafos grandes: streaming não necessário v1; lazy index por `id` e `path`
- Se `domain` data estiver em arquivo separado no UA futuro, loader deve aceitar extensão via config

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Schema UA instável | Fixture de 2 formatos; testes de regressão |
| Grafo ausente | doctor WARN + instrução "run /understand first" |

---

## Demo ao fechar sprint

Em projeto com UA instalado, rodar `graph stats` e mostrar camadas + top 5 hubs.
