# Spike — GitLab Knowledge Graph (`gkg`)

**Data:** 2026-07-01
**Ambiente:** WSL2 Ubuntu (Windows host) — instalação real, não simulada
**Versão testada:** `gkg 0.25.0`

---

## O que foi feito

1. Instalado via script oficial documentado em https://gitlab-org.gitlab.io/rust/knowledge-graph/:
   ```
   curl -fsSL https://gitlab.com/gitlab-org/rust/knowledge-graph/-/raw/main/install.sh | bash
   ```
   Instalação limpa, checksum verificado, ~5s.
2. `gkg index .` no próprio repositório `context-bridge/` (84 arquivos Python):
   indexação em **0,71s** — 464 definições, 584 símbolos importados, 2216 relações.
3. `gkg server start` — sobe um servidor HTTP local (`http://localhost:<porta>`) com:
   - Web UI (Vue) para explorar o grafo visualmente.
   - Endpoint MCP (`/mcp`, streamable HTTP + SSE) com **8 tools**: `read_definitions`,
     `index_project`, `list_projects`, `repo_map`, `search_codebase_definitions`,
     `get_definition`, `import_usage`, `get_references`.
4. Chamado `repo_map` via MCP sobre `context_bridge/sources/` — retorna paths exatos,
   ranges de linha e assinaturas de cada definição.
5. Limpo com `gkg server stop` + `gkg clean` ao final (nenhum dado residual).

## Formato on-disk

- **Parquet** (colunar, formato aberto padrão): `directories.parquet`, `files.parquet`,
  `definitions.parquet`, `imported_symbols.parquet` + tabelas de relacionamento
  (`*_to_*_relationships.parquet`) — todas gravadas em
  `~/.gkg/gkg_workspace_folders/<hash>/<hash>/parquet_files/`.
- **"LadybugDB"** — banco de grafo proprietário do próprio `gkg`
  (`database.kz`) usado para servir as queries via MCP/HTTP. Não documentado
  publicamente; schema inferido apenas pelos logs de indexação (não há
  garantia de estabilidade entre versões).
- Schema observado (nós): `DirectoryNode`, `FileNode`, `DefinitionNode`,
  `ImportedSymbolNode` — todos com `path`. Relações tipadas:
  `DIRECTORY_RELATIONSHIPS`, `FILE_RELATIONSHIPS`, `DEFINITION_RELATIONSHIPS`,
  `IMPORTED_SYMBOL_RELATIONSHIPS`.

## Respostas MCP (amostra)

`repo_map` retorna texto formatado para consumo por LLM (blocos tipo XML com
`<repo-map>`, `<file>`, `<definitions>`), **não** um JSON de grafo bruto:

```
<file>
  <path>context_bridge/sources/lat_md/code_refs.py</path>
  <definitions>
function parse_code_ref L21-28
│ def parse_code_ref(link: WikiLink) -> CodeRef | None:
│     """Turn a wiki link like `[[src/auth.ts#validateToken]]` into a CodeRef.
  </definitions>
</file>
```

Isso é ótimo para um agent LLM consultar diretamente via MCP, mas **não há
comando `gkg export json`** documentado para extrair o grafo completo como
JSON estruturado — a única via pública é o Parquet on-disk (schema não
documentado formalmente) ou o parsing do texto formatado do MCP (frágil,
pensado para prompt, não para máquina).

## Descobertas relevantes

- **Projeto em modo manutenção**: confirmado na própria documentação —
  "This project is in maintenance mode—only critical bug fixes and security
  patches are accepted. The active successor is `gitlab-org/orbit/knowledge-graph`."
  O sucessor ("Orbit KG") é um **projeto diferente**, ainda não testado
  neste spike (repositório não encontrado publicamente em
  `gitlab.com/gitlab-org/orbit/knowledge-graph` no momento da pesquisa —
  provavelmente interno/privado ainda).
- Licença: **MIT** (confirmado via `Cargo.toml: license = "MIT"`).
- 100% self-hosted, sem login/cloud obrigatório.
- Performance excelente (repo pequeno indexado em <1s).

## Checklist go/no-go

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Export JSON/API estável? | **Não** — sem `export json`; Parquet (schema não documentado) ou texto MCP formatado para LLM |
| 2 | Nós com `path` e relações tipadas? | **Sim** — `FileNode`/`DefinitionNode` têm `path`; relações tipadas (`DEFINITION_RELATIONSHIPS` etc.) |
| 3 | Self-hosted sem cloud obrigatória? | **Sim** |
| 4 | Licença compatível MIT? | **Sim** |
| 5 | Esforço ≤ adapter lat.md (~2–3 sem)? | **Não** — exigiria ler Parquet sem schema público documentado (risco de quebra) ou fazer scraping do texto MCP (não estruturado); e o projeto está em manutenção, sucessor (Orbit KG) não testável ainda |

**Resultado: 2 de 5 favoráveis → não atinge o limiar de "go" (≥4).**

## Decisão

**Defer.** Ver [ADR-004](../adr/004-orbit-kg-adapter.md). Reavaliar quando o
sucessor Orbit KG for público ou quando `gkg` documentar um export JSON
estável (o dado técnico já existe — Parquet + grafo tipado — falta só uma
interface pública estável para consumir sem depender de scraping).
