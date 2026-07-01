# Sprint 5 — MCP + Skill + Hooks

**Duração:** 4–5 dias  
**Branch sugerida:** `sprint-5/mcp-skill`  
**Depende de:** Sprint 3, Sprint 4  
**Desbloqueia:** Sprint 6

---

## Meta

Expor a ponte via MCP para Cursor e outros agents, instalar skill auto-trigger, e documentar hooks pós-`/understand`.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S5.1 | `mcp_server.py` — FastMCP, entry `context-bridge mcp` | `context_bridge/mcp_server.py` |
| S5.2 | Tool `bridge_doctor` — mesmo output do CLI doctor | MCP tool |
| S5.3 | Tool `sync_graph_to_engram` — params: dry_run, incremental | MCP tool |
| S5.4 | Tool `enrich_memory_search` — params: query, limit, hops | MCP tool |
| S5.5 | Tool `suggest_memories_from_graph` — params: types | MCP tool |
| S5.6 | Extra `[mcp]` no pyproject — dependência `mcp>=1.2.0` | `pyproject.toml` |
| S5.7 | `config/mcp.json` — template Cursor | `config/mcp.json` |
| S5.8 | `core/installer.py` — detect project, write MCP config, check deps | `context_bridge/core/installer.py` |
| S5.9 | CLI `install --env=auto\|cursor` | `context_bridge/cli.py` |
| S5.10 | `scripts/install.ps1` — wrapper Windows | `scripts/install.ps1` |
| S5.11 | `skill/SKILL.md` — triggers, workflow, exemplos | `skill/SKILL.md` |
| S5.12 | `workflows/sync-after-understand.md` — receita pós-/understand | `workflows/sync-after-understand.md` |
| S5.13 | `workflows/enrich-before-task.md` — receita pré-tarefa | `workflows/enrich-before-task.md` |
| S5.14 | `docs/MCP-SETUP.md` — setup Cursor passo a passo | `docs/MCP-SETUP.md` |
| S5.15 | Testes MCP tools (mock engine, sem rede) | `tests/test_mcp_server.py` |
| S5.16 | Testes installer dry-run | `tests/test_installer.py` |

---

## MCP tools (contrato)

| Tool | Input | Output |
|------|-------|--------|
| `bridge_doctor` | `project_path?` | JSON status checks |
| `sync_graph_to_engram` | `dry_run`, `incremental`, `project_path?` | sync report |
| `enrich_memory_search` | `query`, `limit?`, `hops?` | JSON enrich v1 |
| `suggest_memories_from_graph` | `types?`, `project_path?` | JSON payloads[] |

---

## Skill triggers (exemplos)

Auto-invoke quando o usuário mencionar:

- sincronizar grafo com engram / context bridge
- enriquecer memória com codebase
- ponte engram understand anything
- `/context-bridge`, `/sync-graph`

Workflow resumido na skill:

1. `bridge_doctor`
2. Se grafo OK → `sync_graph_to_engram` (incremental)
3. Antes de tarefa grande → `enrich_memory_search`
4. Persistir decisões manuais → Engram `mem_save` direto

---

## Critérios de aceite

- [ ] `pip install -e ".[mcp]"` + `context-bridge mcp` inicia servidor stdio
- [ ] 4 tools respondem com mocks em pytest
- [ ] `context-bridge install --env=cursor` gera config MCP válida
- [ ] Skill copiada para path documentado (ou instrução clara)
- [ ] `docs/MCP-SETUP.md` permite setup em < 5 min
- [ ] Workflows executáveis de ponta a ponta (documentação)

---

## Comandos de validação

```powershell
pip install -e ".[mcp]"
context-bridge mcp
context-bridge install --dry-run
pytest tests/test_mcp_server.py
```

Config Cursor (manual test):

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

---

## Notas técnicas

- Seguir padrão `agent-reach-tech/mcp_server.py` para consistência
- MCP não substitui Engram MCP — são complementares (Engram = memória nativa; bridge = sync/enrich)
- `install` nunca sobrescreve config MCP existente sem `--force`

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Dois MCPs confundem agent | Skill explica quando usar cada um |
| FastMCP version drift | Pin `mcp>=1.2.0` como agent-reach-tech |

---

## Demo ao fechar sprint

No Cursor: pedir "sincronize o grafo UA com o Engram" e verificar tool call + memórias criadas.
