# Changelog

## 1.2.0 — Sprint 10 (Research spikes Orbit KG/Potpie, Passo 3)

Spikes técnicos reais (instalação de verdade, não simulada — Windows nativo +
WSL2 Ubuntu). Nenhum adapter implementado: ambos os candidatos ficaram em
**defer** (2/5 no checklist go/no-go, abaixo do limiar ≥4 para adopt).

- `docs/research/orbit-kg-spike.md` — GitLab Knowledge Graph (`gkg` 0.25.0)
  instalado e indexado com sucesso via WSL2 (script oficial `curl | bash`);
  servidor MCP com 8 tools testado ao vivo (`repo_map` etc.). Dados bons
  (nós com `path`, relações tipadas em Parquet), mas sem export JSON público
  estável documentado — projeto em manutenção, sucessor Orbit KG ainda não
  público para teste
- `docs/research/potpie-spike.md` — Potpie (`2.0.0b3`, beta): instalação
  nativa Windows falha (`falkordblite`/`redislite` sem suporte `win32`,
  erro real de build capturado); tentativas via WSL2 não completaram
  (footprint pesado ~200MB incl. torch/transformers/scipy); complementado
  com pesquisa documental do README + `docs/context-graph/architecture.md`
  oficiais (ontologia customizável em vez de schema fixo, Python ≥3.12
  exigido pelo backend padrão)
- `docs/adr/004-orbit-kg-adapter.md`, `005-potpie-adapter.md` — decisão
  **defer** para ambos, com checklist go/no-go preenchido e critério de
  reavaliação explícito
- `docs/research/watchlist.md`, `go-no-go-adapters.md` — atualizados com os
  achados reais dos spikes; lat.md marcado como **adotado** (v1.1.0)
- Versão `1.2.0` (sem mudanças em `context_bridge/` — sprint de pesquisa)

## Unreleased — backlog pós-v1.2

- Merge UA + lat.md no mesmo grafo (v1.3)
- `scripts/watch-research.ps1` (monitoramento contínuo da watchlist, opcional na Sprint 10 — não implementado)
- Reavaliar Orbit KG quando o sucessor for público ou `gkg` documentar export JSON estável
- Reavaliar Potpie quando sair do beta e o "Snapshot" JSON tiver schema público

## 1.1.1 — Sprint 9 (Catálogo e watchlist, Passo 4 + início Passo 3)

- `catalog/ai-agents/knowledge/lat-md.md`, `potpie.md` — novas entradas de catálogo
- `catalog/ai-agents/knowledge/understand-anything.md` — link para lat.md em Relacionados
- `catalog/ai-agents/integration/context-bridge.md` — seção "Fontes de grafo" + links lat.md/Potpie
- `manifests/projects.json` — entradas `lat-md` (ativo) e `potpie` (watchlist)
- `README.md` (repo pai) — tabela, diagrama mermaid e combinações úteis atualizados; novo status `watchlist`
- `docs/research/watchlist.md` e `go-no-go-adapters.md` — já existiam do planejamento v1.x; validados contra os critérios de aceite da Sprint 9 (sem mudanças de conteúdo necessárias)
- Validado: `agent-reach-tech catalog search "lat.md"|"potpie"|"context bridge"` retornam as novas entradas
- Versão `1.1.1` (bump apenas documental — nenhuma mudança em `context_bridge/`)

## 1.1.0 — Sprint 8 (Adapter lat.md, Passo 2)

- `context_bridge/sources/` — camada `GraphSource` plugável: `base.py` (Protocol),
  `ua.py` (wrapper sobre `graph/loader.py`), `resolver.py` (`resolve_graph()`,
  `active_source_name()`, `default_graph_ref()`, `graph_file_path()` — escolhe a
  fonte pela prioridade em `config/graph-source.yaml`, sem merge entre fontes)
- `context_bridge/sources/lat_md/` — adapter completo lat.md → `KnowledgeGraph`:
  `wiki_links.py` (parser `[[Target#Section]]`), `code_refs.py` (refs de código),
  `annotations.py` (scan de `@lat: [[...]]` no repositório), `builder.py`
  (`build_lat_graph`, `compute_lat_source_hash`, `write_lat_graph`), `source.py`
  (`LatMdSource`, cache por hash de conteúdo)
- `context-bridge graph import lat-md [--dry-run] [--write PATH]` — novo subcomando CLI
- `sync/engine.py` e `enrich/pipeline.py` agora carregam o grafo via
  `sources.resolver.resolve_graph()` em vez de `graph.loader.load_knowledge_graph()`
  diretamente — é isso que torna lat.md alcançável por `sync`/`enrich`/`suggest`
- `sync/rules.py` — novo campo `graph_ref` (auto-detectado por fonte ativa, ou fixo via
  `sync-rules.yaml`); `sync/mappers/{domains,hubs,layers,tours}.py` deixam de hardcodar
  `.understand-anything/knowledge-graph.json` e recebem `graph_ref` como parâmetro
- `context_bridge/doctor.py` — novos checks `lat-md` (detecta `lat.md/`) e `lat-cli`
  (opcional, `lat` no PATH)
- `config/graph-source.yaml` — prioridade de fontes (`ua` antes de `lat-md` por padrão)
- `docs/SOURCES.md` — arquitetura multi-fonte, mapeamento lat.md → schema UA, limitações
- `docs/adr/002-sources-layer.md`, `003-lat-md-semantic-source.md`
- `tests/fixtures/lat_md_minimal/` + 49 novos testes offline (`tests/test_lat_md_*.py`) —
  cobrem parsers, builder, resolver, e integração sync/enrich/CLI/doctor com lat.md
- 180 testes offline verdes (131 pré-existentes + 49 novos)
- Versão `1.1.0`

## 1.0.1 — Sprint 7 (Operacionalização UA, Passo 1)

- `context_bridge/sync/report.py` — `SyncReport` ganha `graph_age_days`, `duration_seconds` e `counts_by_type` (contagem por mapper: `architecture`/`codebase-map`/`domain`/`tour`); `format_report` lista status e tipo separadamente
- `context_bridge/sync/engine.py` — `run_sync` mede a idade do grafo (`knowledge-graph.json` mtime) e a duração do sync, inclusive no caminho `--incremental` com grafo inalterado
- `scripts/smoke.ps1` — novo passo `enrich` (não-fatal: WARN em vez de FAIL quando o Engram está indisponível, espelhando a semântica WARN/FAIL do `doctor`)
- `skill/SKILL.md` — linka explicitamente os dois workflows e documenta a tabela WARN vs FAIL do `doctor`
- `README.md` — seção "Workflow recomendado" linkando `workflows/sync-after-understand.md` e `workflows/enrich-before-task.md`
- `docs/ARCHITECTURE.md` — seção "Operational flow (post-v1.0)" com a tabela de fases, a semântica WARN/FAIL e as novas métricas do relatório de sync
- `tests/test_sync_report.py` — cobre `counts_by_type`, métricas em `to_dict()`/`format_report`, e que `run_sync` as popula
- Versão `1.0.1`

## 1.0.0 — Sprint 6 (Release v1.0)

- `docs/ARCHITECTURE.md` — overview, módulos, fluxos sync/enrich, config, testes
- README completo: instalação, comandos, matriz de features, dependências
- `.github/workflows/ci.yml` — pytest offline (3.10/3.11/3.12) em push/PR
- `tests/test_integration_e2e.py` — fluxo completo doctor → sync → enrich → suggest (offline)
- `tests/test_integration_network.py` — testes opcionais `@network` contra Engram real, auto-skip
- `scripts/smoke.ps1` — pytest offline + doctor + sync --dry-run + suggest + graph stats
- `LICENSE` (MIT)
- Catálogo do repositório pai atualizado (`manifests/projects.json`, `README.md`, `catalog/ai-agents/integration/context-bridge.md)
- Versão `1.0.0`

## 0.6.0 — Sprint 5 (MCP + Skill + Installer)

- `context_bridge/mcp_server.py` — FastMCP, entry `context-bridge mcp`, 4 tools (`bridge_doctor`, `sync_graph_to_engram`, `enrich_memory_search`, `suggest_memories_from_graph`)
- Lógica de cada tool isolada em funções `*_impl` testáveis sem precisar do SDK MCP rodando
- `context_bridge/core/installer.py` — plano de instalação (deps opcionais + merge de `.cursor/mcp.json`), nunca sobrescreve sem `--force`
- CLI `install --env=auto|cursor|none [--dry-run] [--force]`
- `config/mcp.json` — template Cursor
- `scripts/install.ps1` — wrapper Windows
- `skill/SKILL.md`, `workflows/sync-after-understand.md`, `workflows/enrich-before-task.md`, `docs/MCP-SETUP.md`
- Testes: `test_mcp_server.py`, `test_installer.py` (offline, sem rede)

## 0.5.0 — Sprint 4 (Enrich & Suggest)

- `context_bridge/enrich/` — `where_parser` (anchors `#layer`/`#node`/`#domain`/`#tours` + paths soltos), `graph_context` (BFS de vizinhos via `graph.queries.neighbors`), `pipeline` (busca híbrida), `format_md`/`format_json`
- CLI `enrich QUERY [--json] [--hops N] [--limit N] [--node-limit N]`
- `context_bridge/suggest.py` — preview de payloads `mem_save` do grafo, reusando os mappers da Sprint 3 sem efeitos colaterais
- CLI `suggest [--types ...] [--json]`
- `context_bridge/hooks/post_sync.py` — nota markdown opcional pós-`sync`/`enrich` sugerindo o próximo passo
- Testes: `test_enrich_where.py`, `test_enrich_pipeline.py`, `test_suggest.py`

## 0.4.0 — Sprint 3 (Sync grafo → Engram)

- `context_bridge/sync/` — rules (YAML), mappers (layers, hubs, domains, tours), engine, state, incremental, report
- `config/sync-rules.yaml` — regras default configuráveis
- CLI `sync` real: `--dry-run`, `--incremental`, `--force`, `--types`, `--json`, `--verbose`
- Estado incremental em `.context-bridge/sync-state.json` (fingerprint do grafo + hash por topic_key)
- Dedup local (state) + dedup remoto (busca por topic_key) evitam duplicar memórias
- Testes: engine, incremental, e2e (offline, com `FakeEngramClient`)

## 0.3.0 — Sprint 2 (Cliente Engram)

- `context_bridge/engram/` — config, probe, http_client, cli_client, client (facade), payloads, dedup, errors
- `EngramClient` com degradação HTTP (`engram serve`) → CLI (`engram` binário)
- Contrato `mem_save` real (HTTP API documentada: `/health`, `/search`, `/context`, `/sessions`, `/observations`)
- `topic_key_from_parts` / `topic_key_from_graph_node` — chaves estáveis prefixadas `cb-`
- `doctor` agora reporta qual backend Engram está ativo (HTTP ou CLI)
- Testes mock HTTP (urllib) e CLI (subprocess) offline

## 0.2.0 — Sprint 1 (Leitor do grafo UA)

- `context_bridge/graph/` — models, loader, validate, queries, diff overlay
- CLI `graph stats` e `graph node`
- Doctor expandido: validação do grafo UA, node count, idade do arquivo
- Fixtures e testes offline para grafo

## 0.1.0 — Sprint 0 (Fundação)

- Scaffold CLI `context-bridge` com subcomandos stub
- `doctor` — Python, Engram PATH, pasta `.understand-anything/`
- `core/paths.py`, `core/subprocess_runner.py`
- pytest + markers `@network`
