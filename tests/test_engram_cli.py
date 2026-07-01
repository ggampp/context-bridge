from __future__ import annotations

from context_bridge.core.subprocess_runner import RunResult
from context_bridge.engram import cli_client as cli_client_module
from context_bridge.engram.cli_client import EngramCliClient
from context_bridge.engram.errors import EngramError


def _ok(stdout: str) -> RunResult:
    return RunResult(command=[], returncode=0, stdout=stdout, stderr="")


def _fail(stderr: str) -> RunResult:
    return RunResult(command=[], returncode=1, stdout="", stderr=stderr)


def test_is_available_uses_which(monkeypatch):
    monkeypatch.setattr(cli_client_module, "which", lambda b: "/usr/bin/engram")
    assert EngramCliClient().is_available()


def test_version_returns_stdout(monkeypatch):
    monkeypatch.setattr(cli_client_module, "run_command", lambda *a, **k: _ok("engram v0.9.0\n"))
    assert EngramCliClient().version() == "engram v0.9.0"


def test_search_parses_json_output(monkeypatch):
    monkeypatch.setattr(
        cli_client_module,
        "run_command",
        lambda *a, **k: _ok('{"results": [{"id": 1, "topic_key": "cb-x"}]}'),
    )
    results = EngramCliClient().search("query")
    assert results == [{"id": 1, "topic_key": "cb-x"}]


def test_search_falls_back_to_raw_lines(monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, **kwargs):
        calls["n"] += 1
        if "--json" in cmd:
            return _fail("unknown flag --json")
        return _ok("memory one\nmemory two\n")

    monkeypatch.setattr(cli_client_module, "run_command", fake_run)
    results = EngramCliClient().search("query")
    assert results == [{"raw": "memory one"}, {"raw": "memory two"}]


def test_save_builds_expected_command(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return _ok("saved")

    monkeypatch.setattr(cli_client_module, "run_command", fake_run)
    EngramCliClient().save(title="T", content="C", type_="architecture", project="demo", topic_key="cb-x")
    assert captured["cmd"] == [
        "engram",
        "save",
        "T",
        "C",
        "--type",
        "architecture",
        "--project",
        "demo",
        "--topic-key",
        "cb-x",
    ]


def test_save_raises_on_failure(monkeypatch):
    monkeypatch.setattr(cli_client_module, "run_command", lambda *a, **k: _fail("boom"))
    try:
        EngramCliClient().save(title="T", content="C")
        assert False, "expected EngramError"
    except EngramError as e:
        assert "boom" in str(e)
