from __future__ import annotations

from context_bridge.doctor import run_checks, run_doctor


def test_run_checks_python_ok():
    checks = run_checks()
    python = next(c for c in checks if c.name == "python")
    assert python.status == "OK"


def test_run_doctor_on_fixture(sample_project_root, capsys):
    code = run_doctor(sample_project_root)
    out = capsys.readouterr().out
    assert "Context Bridge" in out
    assert "knowledge-graph" in out
    assert code == 0


def test_run_doctor_without_graph(tmp_path, capsys):
    code = run_doctor(tmp_path)
    out = capsys.readouterr().out
    assert "ua-directory" in out
    assert "WARN" in out
    assert code == 0


def test_knowledge_graph_check_counts_nodes(sample_project_root):
    checks = run_checks(sample_project_root)
    kg = next(c for c in checks if c.name == "knowledge-graph")
    assert kg.status == "OK"
    assert "5 nodes" in kg.detail
    assert "7 edges" in kg.detail
