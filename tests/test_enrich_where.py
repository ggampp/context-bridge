from __future__ import annotations

from context_bridge.enrich.where_parser import extract_where_line, parse_where


def test_extract_where_line_basic():
    content = "**What**: did X\n**Why**: because Y\n**Where**: src/auth/login.ts\n**Learned**: none"
    assert extract_where_line(content) == "src/auth/login.ts"


def test_extract_where_line_missing_returns_none():
    assert extract_where_line("**What**: x\n**Why**: y") is None


def test_extract_where_line_empty_content():
    assert extract_where_line("") is None


def test_parse_where_layer_anchor():
    parsed = parse_where(".understand-anything/knowledge-graph.json#layer:api")
    assert parsed.kind == "layer"
    assert parsed.value == "api"


def test_parse_where_node_anchor_with_path_extra():
    parsed = parse_where(".understand-anything/knowledge-graph.json#node:node-router (src/api/router.ts)")
    assert parsed.kind == "node"
    assert parsed.value == "node-router"
    assert parsed.paths == ("src/api/router.ts",)


def test_parse_where_domain_anchor():
    parsed = parse_where(".understand-anything/knowledge-graph.json#domain:auth")
    assert parsed.kind == "domain"
    assert parsed.value == "auth"


def test_parse_where_tours_anchor():
    parsed = parse_where(".understand-anything/knowledge-graph.json#tours")
    assert parsed.kind == "tours"


def test_parse_where_bare_file_paths():
    parsed = parse_where("src/auth/login.ts, src/auth/middleware.ts")
    assert parsed.kind == "path"
    assert "src/auth/login.ts" in parsed.paths
    assert "src/auth/middleware.ts" in parsed.paths


def test_parse_where_unrecognized_text():
    parsed = parse_where("a free-form note with no path")
    assert parsed.kind == "unknown"
    assert parsed.is_empty


def test_parse_where_empty_string():
    parsed = parse_where("")
    assert parsed.kind == "unknown"
    assert parsed.is_empty
