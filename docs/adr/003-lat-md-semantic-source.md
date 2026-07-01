# ADR-003 — lat.md como fonte semântica complementar

**Status:** aceito
**Data:** 2026-07-01
**Decisores:** Sprint 8 (adapter lat.md)

---

## Contexto

[lat.md](https://github.com/1st1/lat.md) representa conhecimento de um
projeto como Markdown com wiki-links (`[[Target#Section]]`) e permite anotar
código-fonte com `// @lat: [[domain#Section]]` para linkar de volta ao
Markdown. É complementar ao Understand Anything (UA): UA deriva um grafo
estrutural automaticamente a partir do código; lat.md é escrito e mantido por
humanos, capturando intenção e conceitos que a análise estrutural não extrai
sozinha.

Sprint 8 pergunta: lat.md deveria **substituir**, **mesclar-se com**, ou
**coexistir** com o UA como fonte de grafo?

## Decisão

lat.md coexiste com UA como uma segunda fonte, sem merge automático:

- `context_bridge/sources/lat_md/` parseia `lat.md/*.md` + anotações `@lat:`
  no repositório e constrói um `KnowledgeGraph` compatível com o schema
  usado por `graph/loader.py::load_graph_json_file`.
- Mapeamento: um arquivo `lat.md/<domain>.md` vira um nó `domain`; cada
  seção `## Heading` vira um nó `concept`; wiki-links para caminhos de
  código (`[[src/foo.ts#symbol]]`) viram nós `file`/`function` + aresta
  `references`; wiki-links entre seções viram `relates_to`; anotações
  `@lat:` no código viram arestas `references` do lado do código.
- O grafo construído é persistido em `.context-bridge/lat-graph.json`
  (gitignored, análogo a `.understand-anything/knowledge-graph.json`) e
  cacheado via hash de conteúdo (`compute_lat_source_hash`) — só é
  reconstruído quando `lat.md/*.md` ou um arquivo anotado muda.
- `config/graph-source.yaml: priority` decide qual fonte vence quando ambas
  estão disponíveis — **UA primeiro por padrão**, para que projetos UA-only
  continuem se comportando exatamente como antes da v1.1.0.
- **Fontes não são mescladas** nesta versão: `sources/resolver.py::resolve_graph()`
  usa a primeira fonte disponível na ordem de prioridade, integralmente.
  Merge UA+lat no mesmo grafo é backlog explícito (v1.3, ver
  `docs/PLANO-SPRINTS.md`).

## Consequências

- Projetos que adotam lat.md ganham `sync`/`enrich`/`suggest` sem escrever
  nenhum código novo — o parser genérico de `lat_md/builder.py` cobre o
  mapeamento descrito acima.
- Limitação conhecida: nós lat.md não populam `layer` (mapper
  `sync/mappers/layers.py` os agrupa todos sob `"unknown"`). Suporte a
  `layer:` via frontmatter é backlog v1.1.1 (ver Sprint 8, seção "Impacto
  nos mappers"); enquanto isso, projetos podem desabilitar o mapper
  `architecture` via `sync-rules.yaml: layers.enabled: false` quando a fonte
  ativa é lat.md.
- `graph_ref` nas memórias sincronizadas (`where=`) aponta para
  `.context-bridge/lat-graph.json` quando lat.md é a fonte ativa, em vez do
  caminho UA — ver ADR-002.
- Fora de escopo v1.1.0: merge UA+lat, escrita bidirecional lat ← Engram,
  substituir o `lat` CLI upstream (`context-bridge` só consome o Markdown).
