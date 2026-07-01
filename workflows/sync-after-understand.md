# Workflow: sincronizar após `/understand`

**Quando usar:** sempre que o grafo do Understand Anything for gerado ou atualizado (`.understand-anything/knowledge-graph.json` mudou).

## Passos

1. Rodar `/understand` (ou equivalente) e confirmar que `.understand-anything/knowledge-graph.json` existe.
2. Checar prerequisitos:

   ```bash
   context-bridge doctor
   ```

   Esperado: `knowledge-graph` em `OK`, `engram` em `OK` (HTTP ou CLI).

3. Sincronizar de forma incremental (não reprocessa se o grafo não mudou):

   ```bash
   context-bridge sync --incremental
   ```

4. Se quiser ver o que seria feito antes de gravar:

   ```bash
   context-bridge sync --dry-run --verbose
   ```

5. Via MCP (equivalente ao passo 3):

   ```json
   { "tool": "sync_graph_to_engram", "args": { "incremental": true } }
   ```

## Resultado esperado

- Memórias do tipo `architecture` (uma por layer), `codebase-map` (hubs), `domain` (uma por domínio) e `tour` (se configurado) aparecem no Engram com `topic_key` prefixado por `cb-`.
- Rodar de novo sem mudanças no grafo → tudo `skipped` (ou sync inteiro pulado com `--incremental`).

## Quando NÃO sincronizar

- Grafo UA não existe ainda (`doctor` mostra `WARN` em `ua-directory`/`knowledge-graph`) — rodar `/understand` primeiro.
- Engram indisponível (`doctor` mostra `WARN`/`FAIL` em `engram`) — usar `sync --dry-run` para validar o output sem precisar do backend.
