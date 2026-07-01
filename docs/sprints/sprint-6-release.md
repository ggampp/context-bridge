# Sprint 6 — Release v1.0

**Duração:** 3–4 dias  
**Branch sugerida:** `sprint-6/release`  
**Depende de:** Sprint 5  
**Desbloqueia:** — (projeto v1.0)

---

## Meta

Consolidar qualidade, documentação, CI e release `context-bridge v1.0.0`, integrando ao catálogo do repositório pai.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S6.1 | `docs/ARCHITECTURE.md` — diagrama módulos, fluxos sync/enrich | `docs/ARCHITECTURE.md` |
| S6.2 | README completo — instalação, comandos, matriz features, deps | `README.md` |
| S6.3 | `CHANGELOG.md` v0.1.0 → v1.0.0 | `CHANGELOG.md` |
| S6.4 | GitHub Actions CI — pytest offline em push/PR | `.github/workflows/ci.yml` |
| S6.5 | Testes integração E2E — sync dry-run + enrich com fixtures | `tests/test_integration_e2e.py` |
| S6.6 | Testes `@network` opcionais — Engram HTTP se disponível | `tests/test_integration_network.py` |
| S6.7 | `scripts/smoke.ps1` — doctor + sync dry-run + enrich | `scripts/smoke.ps1` |
| S6.8 | Atualizar `manifests/projects.json` (repo pai) — entrada context-bridge | `../manifests/projects.json` |
| S6.9 | Atualizar `README.md` (repo pai) — linha na tabela + mapa relações | `../README.md` |
| S6.10 | Entrada catálogo `catalog/ai-agents/integration/context-bridge.md` | catálogo |
| S6.11 | Bump versão `1.0.0` em pyproject | `pyproject.toml` |
| S6.12 | Tag git `context-bridge-v1.0.0` (quando user pedir) | git tag |
| S6.13 | Smoke test manual com agent real — workflow sync-after-understand | checklist |
| S6.14 | LICENSE MIT | `LICENSE` |

---

## Definition of Done v1.0 (checklist final)

- [ ] `pytest` passa offline (CI verde)
- [ ] `context-bridge doctor` útil em projeto sem UA (instruções claras)
- [ ] `sync --dry-run` + `sync` + `enrich` funcionam com fixture
- [ ] MCP 4 tools documentadas e testadas
- [ ] README onboarding < 10 min
- [ ] Catálogo pai atualizado
- [ ] Zero refs a código não implementado

---

## ARCHITECTURE.md (outline)

```
Overview
    CLI → sync/enrich/doctor
    MCP → same stack
Modules
    graph/     → UA JSON
    engram/    → HTTP + CLI
    sync/      → mappers + engine
    enrich/    → hybrid search
Flows
    Post-/understand sync
    Pre-task enrich
Config
    sync-rules.yaml, mcp.json
Tests
    offline vs @network
```

---

## CI mínimo

```yaml
# .github/workflows/ci.yml
- Python 3.10, 3.11, 3.12
- pip install -e ".[dev,mcp]"
- pytest -m "not network"
```

---

## Critérios de aceite

- [ ] CI passa em Windows (ubuntu opcional v1.0)
- [ ] `scripts/smoke.ps1` exit 0 em dev machine
- [ ] CHANGELOG reflete sprints 0–6
- [ ] Catálogo lista context-bridge como projeto local
- [ ] Demo gravada ou checklist manual preenchida

---

## Comandos de validação

```powershell
pytest -m "not network"
.\scripts\smoke.ps1
context-bridge doctor
context-bridge sync --dry-run
context-bridge enrich "test" --json
```

---

## Integração catálogo (repo pai)

Entrada sugerida em `manifests/projects.json`:

```json
{
  "id": "context-bridge",
  "name": "Context Bridge",
  "local_path": "context-bridge/",
  "category": "ai-agents",
  "subcategory": "integration",
  "status": "active",
  "summary": "Ponte Understand Anything → Engram: sync de grafo, enrich híbrido, MCP.",
  "related": ["engram", "understand-anything", "agent-reach-tech"]
}
```

Mapa de relações no README pai:

```
understand-anything --> context-bridge --> engram
agent-reach-tech --> engram
```

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| CI flaky @network | Marker separado; default offline |
| Doc drift | ARCHITECTURE linkado no README |

---

## Demo ao fechar sprint (release)

1. Projeto com `/understand` já rodado
2. `context-bridge install --env=cursor`
3. `context-bridge sync`
4. Nova sessão agent → `enrich "módulo principal"`
5. Verificar memórias no `engram tui`

**Veredito interno:** adotar como padrão Memória + Conhecimento no stack de agents.
