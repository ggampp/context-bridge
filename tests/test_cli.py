from __future__ import annotations

import subprocess
import sys

import pytest

from context_bridge.cli import build_parser, main


def test_build_parser_lists_subcommands():
    parser = build_parser()
    sub = next(a for a in parser._actions if a.dest == "command")
    names = set(sub.choices.keys())
    assert names >= {"doctor", "sync", "enrich", "suggest", "install", "mcp", "graph"}


def test_main_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_sync_without_graph_returns_one(tmp_path):
    assert main(["sync", "--project", str(tmp_path), "--dry-run"]) == 1


def test_sync_dry_run_on_fixture(sample_project_root):
    assert main(["sync", "--project", str(sample_project_root), "--dry-run", "--json"]) == 0


def test_suggest_on_fixture(sample_project_root):
    assert main(["suggest", "--project", str(sample_project_root), "--json"]) == 0


def test_suggest_without_graph_returns_one(tmp_path):
    assert main(["suggest", "--project", str(tmp_path)]) == 1


def test_graph_stats_on_fixture(sample_project_root):
    assert main(["graph", "stats", "--project", str(sample_project_root), "--json"]) == 0


def test_graph_node_on_fixture(sample_project_root):
    assert main(["graph", "node", "src/auth/login.ts", "--project", str(sample_project_root)]) == 0


def test_graph_node_missing_returns_one(sample_project_root):
    assert main(["graph", "node", "missing.ts", "--project", str(sample_project_root)]) == 1


def test_cli_entrypoint_help():
    result = subprocess.run(
        [sys.executable, "-m", "context_bridge.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "context-bridge" in result.stdout
