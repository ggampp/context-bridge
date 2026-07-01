# ADR-002 — Camada `sources/` (GraphSource plugável)

**Status:** aceito
**Data:** 2026-07-01
**Decisores:** Sprint 8 (adapter lat.md)

---

## Contexto

Até a v1.0.0, `context_bridge/graph/loader.py::load_knowledge_graph` era o único
ponto de entrada para carregar um `KnowledgeGraph`, e presumia sempre o schema
do Understand Anything (UA) em `.understand-anything/knowledge-graph.json`.

A Sprint 8 introduz **lat.md** como segunda fonte de grafo. `sync`, `enrich` e
`suggest` não devem saber qual fonte alimentou o grafo — só devem operar sobre
`KnowledgeGraph`. Era necessário um ponto de indireção único.

## Decisão

Introduzir `context_bridge/sources/`:

- `sources/base.py` — `Protocol GraphSource` com `available(project_root)` e
  `load(project_root, *, use_cache)`.
- `sources/ua.py::UASource` — adapter fino sobre `graph/loader.py`.
- `sources/lat_md/` — parser completo lat.md → `KnowledgeGraph`.
- `sources/resolver.py::resolve_graph()` — tenta cada fonte, em ordem de
  prioridade (`config/graph-source.yaml`), e usa a primeira disponível.
  Fontes **não são mescladas**.

**Desvio deliberado do desenho original da Sprint 8:** o plano inicial dizia
"refactor loader UA para `sources/ua.py`" com `graph/loader.py` *delegando*
para lá. Na implementação, a direção foi mantida invertida —
`sources/ua.py::UASource` é quem delega para `graph/loader.py`, não o
contrário — porque:

1. `graph/loader.py::load_knowledge_graph` já é importado diretamente por
   `cli.py` (comandos `graph stats`/`graph node`, que são explicitamente
   "consultar o grafo UA") e por boa parte da suite de testes pré-Sprint-8.
2. Inverter a direção exigiria mover toda a lógica de parsing/validação de
   `loader.py` para `sources/ua.py` e depois reexportar de volta — puro
   churn mecânico, sem ganho funcional, com risco real de regressão nos 131
   testes existentes.
3. O objetivo do Protocol (permitir que `sync`/`enrich` troquem de fonte sem
   saber o schema on-disk) já é alcançado com o wrapper fino — a direção da
   dependência interna é um detalhe de implementação, não um requisito de
   arquitetura.

`sync/engine.py::run_sync` e `enrich/pipeline.py::run_enrich` foram
atualizados para carregar o grafo via `sources.resolver.resolve_graph()` em
vez de `graph.loader.load_knowledge_graph()` diretamente — é isso que torna
lat.md realmente alcançável pelo pipeline (ver ADR-003).

## Consequências

- `sources/` é o único lugar que decide "qual fonte, para este projeto".
- Novas fontes (Orbit KG, Potpie — Sprint 10) implementam `GraphSource` e se
  registram em `sources/resolver.py::_REGISTRY`, sem tocar em `sync/`,
  `enrich/` ou `cli.py` além do necessário para importação inicial.
- `graph/loader.py` continua sendo o parser canônico do schema UA; não há
  segunda implementação de parsing UA em `sources/ua.py`.
- `where=` gravado pelos mappers de sync passa a refletir a fonte ativa via
  `sync/rules.py::DEFAULT_GRAPH_REF` / `sources/resolver.py::default_graph_ref()`
  em vez de um prefixo `.understand-anything/...` fixo.
