# Fontes de grafo (multi-fonte, v1.1.0+)

Context Bridge lê um `KnowledgeGraph` de uma **fonte plugável** antes de
rodar `sync`/`enrich`/`suggest`. Até a v1.0.0 a única fonte era o
Understand Anything (UA). A partir da v1.1.0, **lat.md** é uma segunda
fonte suportada. Ver [ADR-002](adr/002-sources-layer.md) e
[ADR-003](adr/003-lat-md-semantic-source.md) para o histórico da decisão.

---

## Como a fonte é escolhida

```
context_bridge/sources/
├── base.py       # Protocol GraphSource (available/load)
├── ua.py         # UASource — wrapper sobre graph/loader.py
├── resolver.py   # resolve_graph() — escolhe a fonte ativa
└── lat_md/       # parser lat.md/*.md + @lat: annotations → KnowledgeGraph
```

`sources/resolver.py::resolve_graph(project)`:

1. Lê `config/graph-source.yaml: priority` (padrão: `[ua, lat-md]`).
2. Para cada nome na ordem, testa `source.available(project_root)`.
3. Usa a **primeira fonte disponível** — fontes **não são mescladas**.
4. Se nenhuma estiver disponível, cai no loader UA (para preservar a
   mensagem de erro `FileNotFoundError` original).

`sync/engine.py::run_sync` e `enrich/pipeline.py::run_enrich` chamam
`resolve_graph()` — nenhum dos dois sabe se o grafo veio de
`.understand-anything/knowledge-graph.json` ou `.context-bridge/lat-graph.json`.

## Fonte: Understand Anything (`ua`)

- Disponível quando `.understand-anything/knowledge-graph.json` existe.
- Implementação: `sources/ua.py::UASource` delega para
  `graph/loader.py::load_knowledge_graph` (parser canônico, inalterado).
- `context-bridge` **nunca** executa `/understand` — isso é responsabilidade
  do UA (ver `AIMemory/knowledge/ua-primary-source.md`).

## Fonte: lat.md (`lat-md`)

- Disponível quando existe `.context-bridge/lat-graph.json` **ou** um
  diretório `lat.md/` no projeto.
- Implementação: `sources/lat_md/`:
  - `wiki_links.py` — parser de `[[Target]]`, `[[Target#Section]]`,
    `[[Target#Section|Display]]`, `[[#Section]]` (referência na mesma
    seção/arquivo).
  - `code_refs.py` — reconhece links que apontam para código
    (`[[src/foo.ts#symbol]]`, heurística: contém `/` ou extensão de
    código conhecida) e gera um id de nó estável (`lat-code-<slug>[-<slug>]`).
  - `annotations.py::scan_annotations` — varre o repositório procurando
    `@lat: [[...]]` em comentários de código-fonte (qualquer estilo de
    comentário), ignorando diretórios comuns (`node_modules`, `.git`, etc.).
  - `builder.py::build_lat_graph` — monta o `KnowledgeGraph`.
  - `source.py::LatMdSource` — implementa `GraphSource`; usa
    `compute_lat_source_hash` para decidir se reconstrói
    `.context-bridge/lat-graph.json` ou reaproveita o cache.

### Mapeamento lat.md → schema UA

| Elemento lat.md | Nó/aresta | Detalhe |
|-----------------|-----------|---------|
| `lat.md/<domain>.md` | nó `domain`, id `lat-<slug>` | `summary` = texto antes do primeiro `##` |
| `## Heading` dentro do arquivo | nó `concept`, id `lat-<domain>-<slug-do-heading>` | `summary` = corpo da seção (até 500 chars) |
| domínio → seção | aresta `contains` | |
| `[[src/foo.ts#symbol]]` numa seção | nó `file`/`function` + aresta `references` | tipo `function` se houver `#symbol`, senão `file` |
| `[[OutroDominio#Section]]` numa seção | aresta `relates_to` | liga a seção de origem à seção alvo |
| `// @lat: [[domain#Section]]` no código | aresta `references` (código → seção) | escaneado em qualquer arquivo de código sob o projeto |

Saída: `.context-bridge/lat-graph.json`, com `metadata.source = "lat-md"` e
`metadata.source_hash` (fingerprint de `lat.md/*.md` + arquivos anotados,
usado para invalidar o cache).

### `graph_ref` nas memórias sincronizadas

O campo `where=` de cada memória gerada por `sync` inclui um prefixo de
"onde olhar" (ex.: `.understand-anything/knowledge-graph.json#domain:auth`).
Esse prefixo é resolvido automaticamente por
`sources/resolver.py::default_graph_ref(source_name)`:

| Fonte ativa | `graph_ref` padrão |
|-------------|---------------------|
| `ua` | `.understand-anything/knowledge-graph.json` |
| `lat-md` | `.context-bridge/lat-graph.json` |

Pode ser sobrescrito globalmente com `sync-rules.yaml: graph_ref: "<valor>"`.

## Comandos

```powershell
# Gerar/atualizar .context-bridge/lat-graph.json a partir de lat.md/
context-bridge graph import lat-md --project <dir> --dry-run
context-bridge graph import lat-md --project <dir> --write .context-bridge/lat-graph.json

# sync/enrich/suggest usam a fonte ativa automaticamente — nenhuma flag extra
context-bridge sync --project <dir> --incremental
context-bridge enrich "fluxo OAuth" --project <dir>

# doctor detecta lat.md/ e (opcionalmente) o CLI `lat` no PATH
context-bridge doctor --project <dir>
```

## Configuração

`config/graph-source.yaml`:

```yaml
priority:
  - ua
  - lat-md
```

`config/sync-rules.yaml` (trecho relevante):

```yaml
graph_ref: ""   # "" = auto-detectar por fonte ativa; ou um valor fixo
```

## Limitações conhecidas

- **Sem merge**: se um projeto tem UA *e* lat.md, apenas UA é usado por
  padrão (mude `priority` para inverter). Merge no mesmo grafo é backlog
  v1.3.
- **`layer` não populado por lat.md**: nós lat.md não têm `layer`, então o
  mapper `architecture` (`sync/mappers/layers.py`) os agrupa sob
  `"unknown"`. Suporte a `layer:` via frontmatter é backlog v1.1.1;
  enquanto isso, desabilite via `sync-rules.yaml: layers.enabled: false`
  se isso gerar ruído.
- **Sem escrita bidirecional**: `context-bridge` nunca escreve em
  `lat.md/*.md` nem substitui o CLI `lat` upstream — apenas consome o
  Markdown e as anotações `@lat:`.
- **Performance**: `scan_annotations` varre todo o repositório em busca de
  `@lat:` a cada `graph import lat-md` (limitado a extensões de código
  conhecidas). Em repositórios muito grandes isso pode ficar lento — não
  há cache de escaneamento de anotações além do hash agregado usado para
  decidir se o grafo inteiro precisa ser reconstruído.
