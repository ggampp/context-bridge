# Workflow: enriquecer antes de uma tarefa

**Quando usar:** antes de iniciar uma tarefa não-trivial em um projeto que já tem memórias Engram e/ou grafo UA sincronizado.

## Passos

1. Formular a query com palavras-chave da tarefa (ex.: "fluxo de pagamento", "autenticação", nome de um módulo).

   ```bash
   context-bridge enrich "fluxo de pagamento" --json
   ```

2. Ler o campo `memories[]` — decisões e contexto já documentados no Engram.
3. Ler o campo `graph_nodes[]` — arquivos/módulos relacionados (1 hop por padrão; usar `--hops 2` se precisar de mais contexto).
4. Se nenhuma memória aparecer:
   - Rodar `context-bridge sync --incremental` (talvez o grafo nunca tenha sido sincronizado).
   - Ou seguir a tarefa e, ao final, persistir a decisão via Engram `mem_save` diretamente.

## Via MCP

```json
{ "tool": "enrich_memory_search", "args": { "query": "fluxo de pagamento", "hops": 1, "limit": 10 } }
```

## Formato de saída (JSON v1)

```json
{
  "version": 1,
  "query": "fluxo de pagamento",
  "graph_available": true,
  "memories": [
    {
      "id": 42,
      "title": "Domain: payments",
      "type": "domain",
      "topic_key": "cb-domain-payments",
      "content": "...",
      "graph_nodes": [{ "id": "...", "label": "...", "path": "...", "layer": "...", "summary": "..." }],
      "graph_note": null
    }
  ],
  "graph_nodes": [ /* união de todos os nós relacionados, deduplicada */ ]
}
```

## Dicas

- `--limit` controla quantas memórias Engram são buscadas (default 10).
- `--node-limit` controla quantos nós de grafo aparecem por âncora (default 15).
- Memórias sem `where` resolvível ainda aparecem — `graph_note` explica o motivo.
