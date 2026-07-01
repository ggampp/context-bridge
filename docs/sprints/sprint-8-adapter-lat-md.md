# Sprint 8 — Adapter lat.md (Passo 2)

**Versão alvo:** v1.1.0  
**Duração:** 2–3 semanas  
**Branch sugerida:** `sprint-8/adapter-lat-md`  
**Depende de:** Sprint 7  
**Desbloqueia:** Sprint 10 (adapters Orbit/Potpie reutilizam camada `sources/`)

---

## Meta

Permitir que projetos com **`lat.md/`** alimentem o mesmo pipeline sync/enrich, produzindo JSON compatível com `graph/loader.py`. lat.md é **fonte semântica complementar** ao UA — não substituto.

**Passo do roadmap:** [Passo 2 — Médio prazo](../PLANO-SPRINTS.md#passo-2--médio-prazo-adapter-latmd--knowledge-graphjson)

---

## Arquitetura alvo

```
lat.md/**/*.md  +  @lat: annotations
         ↓
  sources/lat_md.py  (parser + builder)
         ↓
.context-bridge/lat-graph.json   (schema UA-compatible)
         ↓
  sync / enrich / suggest  (inalterados)
         ↓
       Engram
```

Nova camada `context_bridge/sources/`:

| Módulo | Responsabilidade |
|--------|------------------|
| `sources/base.py` | Protocol `GraphSource` |
| `sources/ua.py` | Refactor do loader UA atual |
| `sources/lat_md.py` | Adapter lat.md → `KnowledgeGraph` |
| `sources/resolver.py` | Prioridade configurável UA vs lat |

Config: `config/graph-source.yaml`

---

## Mapeamento lat.md → schema UA

| Elemento lat.md | Nó UA | Campos principais |
|-----------------|-------|-------------------|
| `lat.md/auth.md` | domain | `id=lat-auth`, `domain=auth` |
| Seção `[[auth#OAuth Flow]]` | concept | `summary=<texto>` |
| `[[src/auth.ts#validateToken]]` | file/function | `path`, `label` |
| `// @lat: [[auth#OAuth Flow]]` | edge | `type=references` |
| Wiki link entre seções | edge | `type=relates_to` |

Saída: `.context-bridge/lat-graph.json` + `metadata.source=lat-md`.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S8.1 | Protocol `GraphSource` + resolver de fonte | `context_bridge/sources/` |
| S8.2 | Refactor loader UA para `sources/ua.py` | `context_bridge/graph/loader.py` (delegar) |
| S8.3 | Parser wiki links `[[file#Section]]` | `sources/lat_md/wiki_links.py` |
| S8.4 | Parser refs código `[[src/foo.ts#sym]]` | `sources/lat_md/code_refs.py` |
| S8.5 | Scan anotações `@lat:` no repo | `sources/lat_md/annotations.py` |
| S8.6 | Builder → `KnowledgeGraph` | `sources/lat_md/builder.py` |
| S8.7 | CLI `graph import lat-md [--dry-run] [--write PATH]` | `context_bridge/cli.py` |
| S8.8 | `config/graph-source.yaml` — prioridade UA / lat-md | `config/graph-source.yaml` |
| S8.9 | `sync-rules.yaml` — `graph_ref` configurável (substituir hardcode em mappers) | `sync/mappers/*.py`, `sync/rules.py` |
| S8.10 | Sync incremental: hash de `lat.md/` + arquivos `@lat:` | `sync/incremental.py`, `sync/state.py` |
| S8.11 | Doctor: detecta `lat.md/`, opcional `lat` CLI no PATH | `context_bridge/doctor.py` |
| S8.12 | Fixtures + testes offline | `tests/fixtures/lat_md_minimal/`, `tests/test_lat_md_*.py` |
| S8.13 | Doc `docs/SOURCES.md` — multi-fonte, mapeamento, limitações | `docs/SOURCES.md` |
| S8.14 | ADR-002 e ADR-003 em `docs/adr/` | `docs/adr/002-sources-layer.md`, `003-lat-md-semantic-source.md` |
| S8.15 | Bump versão `1.1.0` | `pyproject.toml`, `CHANGELOG.md` |

---

## Impacto nos mappers

| Mapper | Com lat.md |
|--------|------------|
| `domains.py` | Domínios = arquivos top-level em `lat.md/` |
| `layers.py` | Desabilitado ou via frontmatter `layer:` (backlog v1.1.1) |
| `hubs.py` | Grau = wiki links + backlinks `@lat:` |
| `tours.py` | Seções com `tour: true` no frontmatter |

Campo `where` usa `graph_ref` de `sync-rules.yaml` (default UA).

---

## Fora de escopo v1.1.0

- Merge UA + lat no mesmo grafo (v1.2+)
- Escrita bidirecional lat ← Engram
- Substituir `lat check` — apenas consumir Markdown

---

## Critérios de aceite

- [x] `graph import lat-md` gera JSON válido (`validate_graph()` OK)
- [x] `sync` grava memórias `domain` a partir de `lat.md/auth.md`
- [x] `enrich` resolve `#node:lat-auth-oauth-flow` e expande 1 hop
- [x] UA + lat coexistem: `graph-source.yaml` define qual fonte usar
- [x] `pytest -m "not network"` verde (180 testes)
- [x] `docs/SOURCES.md` publicado
- [x] CHANGELOG v1.1.0 publicado

---

## Comandos de validação

```powershell
context-bridge graph import lat-md --project tests/fixtures/lat_md_minimal --dry-run
context-bridge graph import lat-md --project tests/fixtures/lat_md_minimal --write .context-bridge/lat-graph.json
context-bridge sync --project tests/fixtures/lat_md_minimal --dry-run
pytest tests/test_lat_md_*.py -v
```

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Schema lat.md evolui | Versionar fixtures; parser tolerante |
| Duplicata UA + lat no Engram | `topic_key_prefix` + `graph_ref` distintos |
| Performance em repos grandes | Hash incremental; limitar scan `@lat:` a paths do projeto |

---

## Demo ao fechar sprint

1. Repo com `lat.md/` minimal (fixture ou real)
2. `graph import lat-md` → `.context-bridge/lat-graph.json`
3. `sync --incremental` → memórias domain no Engram (ou dry-run)
4. `enrich "OAuth flow"` → nós lat + memórias
