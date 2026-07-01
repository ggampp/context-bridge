from __future__ import annotations

import builtins
import importlib.util
import json
from unittest.mock import patch

from context_bridge.engram.errors import EngramConnectionError
from context_bridge.enrich.pipeline import EnrichResult


def test_mcp_server_module_importable():
    spec = importlib.util.find_spec("context_bridge.mcp_server")
    assert spec is not None


def test_run_mcp_without_sdk_returns_error(capsys):
    real_import = builtins.__import__

    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "mcp.server.fastmcp" or (fromlist and "fastmcp" in fromlist):
            raise ImportError("No module named 'mcp.server.fastmcp'")
        return real_import(name, globals, locals, fromlist, level)

    from context_bridge.mcp_server import run_mcp

    with patch("builtins.__import__", side_effect=mock_import):
        code = run_mcp()
    captured = capsys.readouterr()
    assert code == 1
    assert "MCP SDK" in captured.err


def test_bridge_doctor_impl_returns_json_list(sample_project_root):
    from context_bridge.mcp_server import bridge_doctor_impl

    data = json.loads(bridge_doctor_impl(str(sample_project_root)))
    assert isinstance(data, list)
    names = {item["name"] for item in data}
    assert {"python", "engram", "ua-directory", "knowledge-graph"} <= names


def test_sync_graph_to_engram_impl_dry_run(sample_project_root):
    from context_bridge.mcp_server import sync_graph_to_engram_impl

    data = json.loads(sync_graph_to_engram_impl(str(sample_project_root), dry_run=True))
    assert "counts" in data
    assert "error" not in data


def test_sync_graph_to_engram_impl_missing_graph_returns_error(tmp_path):
    from context_bridge.mcp_server import sync_graph_to_engram_impl

    data = json.loads(sync_graph_to_engram_impl(str(tmp_path), dry_run=True))
    assert "error" in data


def test_enrich_memory_search_impl_returns_formatted_json(monkeypatch, sample_project_root):
    from context_bridge import mcp_server

    def fake_run_enrich(project, query, *, limit=10, hops=1, **_):
        return EnrichResult(query=query, memories=[], graph_available=True)

    monkeypatch.setattr(mcp_server, "run_enrich", fake_run_enrich)
    data = json.loads(mcp_server.enrich_memory_search_impl("router", str(sample_project_root)))
    assert data["version"] == 1
    assert data["query"] == "router"
    assert data["memories"] == []


def test_enrich_memory_search_impl_handles_engram_error(monkeypatch, sample_project_root):
    from context_bridge import mcp_server

    def fake_run_enrich(*_args, **_kwargs):
        raise EngramConnectionError("unreachable")

    monkeypatch.setattr(mcp_server, "run_enrich", fake_run_enrich)
    data = json.loads(mcp_server.enrich_memory_search_impl("router", str(sample_project_root)))
    assert "error" in data


def test_suggest_memories_from_graph_impl_filters_types(sample_project_root):
    from context_bridge.mcp_server import suggest_memories_from_graph_impl

    data = json.loads(suggest_memories_from_graph_impl(str(sample_project_root), types="architecture"))
    assert data
    assert all(p["type"] == "architecture" for p in data)


def test_suggest_memories_from_graph_impl_missing_graph_returns_error(tmp_path):
    from context_bridge.mcp_server import suggest_memories_from_graph_impl

    data = json.loads(suggest_memories_from_graph_impl(str(tmp_path)))
    assert isinstance(data, dict)
    assert "error" in data
