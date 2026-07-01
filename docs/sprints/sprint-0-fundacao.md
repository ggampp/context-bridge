# Sprint 0 — Fundação

**Duração:** 2–3 dias  
**Branch sugerida:** `sprint-0/fundacao`  
**Depende de:** —  
**Desbloqueia:** Sprint 1, Sprint 2

---

## Meta

Criar o scaffold do projeto `context-bridge`: pacote Python instalável, CLI mínima, estrutura de testes e `doctor` stub que valida pré-requisitos básicos.

---

## Entregáveis

| ID | Tarefa | Arquivo / módulo |
|----|--------|------------------|
| S0.1 | Criar `pyproject.toml` — nome, versão `0.1.0`, deps, script CLI | `pyproject.toml` |
| S0.2 | Estrutura de pacote `context_bridge/` | `context_bridge/__init__.py` |
| S0.3 | CLI com subcomandos stub: `doctor`, `sync`, `enrich`, `suggest`, `install`, `mcp` | `context_bridge/cli.py` |
| S0.4 | `doctor.py` — checar: Python ≥3.10, `engram` no PATH, pasta `.understand-anything/` existe | `context_bridge/doctor.py` |
| S0.5 | `core/paths.py` — resolver raiz do projeto, caminhos UA e Engram data dir | `context_bridge/core/paths.py` |
| S0.6 | `core/subprocess_runner.py` — wrapper seguro (reutilizar padrão agent-reach-tech) | `context_bridge/core/subprocess_runner.py` |
| S0.7 | Setup pytest: `tests/`, marker `@network`, fixture `sample_project_root` | `tests/conftest.py` |
| S0.8 | Testes: CLI `--help`, doctor offline (sem engram mock) | `tests/test_cli.py`, `tests/test_doctor.py` |
| S0.9 | `.gitignore` — `__pycache__`, `.pytest_cache`, `dist/`, `.venv/` | `.gitignore` |
| S0.10 | `CHANGELOG.md` v0.1.0 — sprint 0 | `CHANGELOG.md` |

---

## Estrutura alvo ao fim da sprint

```
context-bridge/
├── pyproject.toml
├── CHANGELOG.md
├── README.md
├── context_bridge/
│   ├── __init__.py
│   ├── cli.py
│   ├── doctor.py
│   └── core/
│       ├── __init__.py
│       ├── paths.py
│       └── subprocess_runner.py
└── tests/
    ├── conftest.py
    ├── test_cli.py
    └── test_doctor.py
```

---

## Critérios de aceite

- [ ] `pip install -e ".[dev]"` instala sem erro
- [ ] `context-bridge --help` lista todos os subcomandos
- [ ] `context-bridge doctor` roda e reporta status (OK/WARN/FAIL por check)
- [ ] `pytest` passa offline
- [ ] Nenhum import circular entre módulos

---

## Comandos de validação

```powershell
cd context-bridge
python -m pip install -e ".[dev]"
pytest
context-bridge doctor
context-bridge sync --help
```

---

## Notas técnicas

- Versão inicial `0.1.0`; release `1.0.0` só na Sprint 6
- `doctor` deve ser **read-only** — nunca altera Engram ou grafo
- Subcomandos ainda não implementados retornam exit code 2 + mensagem "not implemented in v0.1"

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Copiar demais do agent-reach-tech | Só reutilizar `subprocess_runner` e padrão CLI; resto mínimo |

---

## Demo ao fechar sprint

Rodar `context-bridge doctor` em `projetos_exemplo/` e mostrar checks de Engram + pasta `.understand-anything/` (mesmo que ausente — WARN claro).
