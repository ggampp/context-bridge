# MCP Setup — Context Bridge v1.0

## Instalação

```powershell
pip install -e ".[mcp]"
# ou
pip install context-bridge[mcp]
```

Verificar:

```powershell
context-bridge doctor
context-bridge sync --dry-run
```

## Cursor

Copie ou mescle em `.cursor/mcp.json` na raiz do projeto:

```json
{
  "mcpServers": {
    "context-bridge": {
      "command": "context-bridge",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

Ou gere automaticamente:

```powershell
context-bridge install --env=cursor
```

Reinicie o Cursor após salvar. O servidor usa transporte stdio.

Template em `context-bridge/config/mcp.json`.

## Claude Desktop / outros clientes MCP

```json
{
  "mcpServers": {
    "context-bridge": {
      "command": "context-bridge",
      "args": ["mcp"]
    }
  }
}
```

Certifique-se de que `context-bridge` está no PATH (após `pip install`).

## Tools disponíveis

| Tool | Uso |
|------|-----|
| `bridge_doctor(project_path?)` | Status de Python, Engram (HTTP/CLI) e grafo UA |
| `sync_graph_to_engram(project_path?, dry_run?, incremental?, force?)` | Sincroniza grafo → Engram |
| `enrich_memory_search(query, project_path?, limit?, hops?)` | Busca híbrida memória + grafo |
| `suggest_memories_from_graph(project_path?, types?)` | Pré-visualiza payloads sem gravar |

## Fluxo recomendado para agents

1. `bridge_doctor` — checar prerequisitos
2. `sync_graph_to_engram(incremental=true)` — após `/understand`
3. `enrich_memory_search` — antes de tarefas não-triviais
4. Engram `mem_save` direto — para decisões que não vêm do grafo

## Instalação programática

```powershell
context-bridge install --env=cursor --dry-run   # ver plano
context-bridge install --env=cursor             # aplicar
context-bridge install --env=cursor --force     # sobrescrever entrada existente
```

`install` nunca sobrescreve uma entrada `context-bridge` já existente em `.cursor/mcp.json` sem `--force`.

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `MCP SDK not installed` | `pip install context-bridge[mcp]` |
| Comando não encontrado | `pip install -e .` e reiniciar terminal |
| `engram` indisponível em `doctor` | Rodar `engram serve` ou instalar a CLI no PATH (opcional — sync funciona em `--dry-run` sem isso) |
| Grafo UA não encontrado | Rodar `/understand` no projeto primeiro |
