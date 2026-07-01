# Watchlist — fontes de grafo alternativas

Registro de evolução para adapters futuros do Context Bridge.  
**Cadência:** revisão quinzenal — próxima revisão: **2026-07-15**

Gerenciado nas Sprints [9](sprints/sprint-9-catalogo-watchlist.md) e [10](sprints/sprint-10-research-adapters.md).

---

## Entradas

| Data | Projeto | Versão/tag | Achado | Impacto adapter | Decisão |
|------|---------|------------|--------|-----------------|---------|
| 2026-06-30 | [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) | main | Fonte primária v1.0; 69k★; schema nativo | — | **adotar** (v1.0) |
| 2026-06-30 | [lat.md](https://github.com/1st1/lat.md) | main | Grafo semântico Markdown; complementa UA | alto | em desenvolvimento (Sprint 8) |
| 2026-07-01 | [lat.md](https://github.com/1st1/lat.md) | main, MIT, 1.7k★ | Adapter implementado e testado (49 testes) — `sources/lat_md/` | alto | **adotado** (v1.1.0) |
| 2026-06-30 | [GitLab GKG](https://gitlab.com/gitlab-org/rust/knowledge-graph) | maintenance | MCP + `gkg index`; sucessor Orbit KG | alto | observar |
| 2026-07-01 | [GitLab GKG](https://gitlab.com/gitlab-org/rust/knowledge-graph) | v0.25.0, MIT, maintenance | Spike real (instalado + indexado): dados bons (path + relações tipadas) mas sem export JSON público estável (Parquet interno não documentado); projeto em manutenção, sucessor Orbit KG ainda não público | alto | **defer** (2/5 no go/no-go — [ADR-004](../adr/004-orbit-kg-adapter.md)) |
| 2026-06-30 | [Potpie](https://github.com/potpie-ai/potpie) | main | Living context graph; daemon + `potpie ui` | médio | observar |
| 2026-07-01 | [Potpie](https://github.com/potpie-ai/potpie) | v2.0.0b3 (beta), Apache-2.0 | Spike real: instalação nativa Windows falha (`falkordblite`/`redislite` sem suporte win32); ontologia customizável em vez de schema fixo; footprint pesado (~200MB deps) | médio | **defer** (2/5 no go/no-go — [ADR-005](../adr/005-potpie-adapter.md)) |
| 2026-06-30 | [Pharaoh](https://pharaoh.so/) | SaaS | MCP cloud; parser OSS mínimo | baixo | evitar (base OSS) |
| 2026-06-30 | [GraphMyCode](https://graphmycode.com) | web | Browser-only; export `.md` | baixo | observar |

---

## Como atualizar

1. Rodar pesquisa via `agent-reach-tech` (ver Sprint 10).
2. Adicionar linha com data ISO e decisão: `adotar | observar | evitar | defer | em desenvolvimento`.
3. Se decisão mudar para **adotar**, abrir ADR em `docs/adr/` antes de codificar.

---

## Snapshots (opcional)

Arquivos JSON gerados por `scripts/watch-research.ps1` (Sprint 10):

```
docs/research/snapshots/
  potpie-YYYY-MM-DD.json
  orbit-kg-YYYY-MM-DD.json
```
