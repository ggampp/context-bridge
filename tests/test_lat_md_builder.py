from __future__ import annotations

import pytest

from context_bridge.graph.validate import validate_graph
from context_bridge.sources.lat_md.builder import (
    build_lat_graph,
    compute_lat_source_hash,
    lat_graph_path,
    serialize_graph,
    split_sections,
    write_lat_graph,
)


def test_build_lat_graph_produces_expected_nodes(lat_md_project_root):
    graph = build_lat_graph(lat_md_project_root)
    node_ids = {n.id for n in graph.nodes}
    assert "lat-auth" in node_ids
    assert "lat-auth-oauth-flow" in node_ids
    assert "lat-auth-session-refresh" in node_ids
    assert "lat-billing" in node_ids
    assert "lat-billing-plan-limits" in node_ids
    assert "lat-code-src-auth-ts-validatetoken" in node_ids


def test_build_lat_graph_produces_expected_edges(lat_md_project_root):
    graph = build_lat_graph(lat_md_project_root)
    edges = {(e.source, e.target, e.type) for e in graph.edges}
    assert ("lat-auth", "lat-auth-oauth-flow", "contains") in edges
    assert ("lat-auth-oauth-flow", "lat-code-src-auth-ts-validatetoken", "references") in edges
    assert ("lat-auth-oauth-flow", "lat-billing-plan-limits", "relates_to") in edges
    # the @lat: annotation in src/auth.ts links back to the same concept
    assert ("lat-code-src-auth-ts", "lat-auth-oauth-flow", "references") in edges


def test_build_lat_graph_is_valid_against_graph_schema(lat_md_project_root):
    graph = build_lat_graph(lat_md_project_root)
    result = validate_graph(graph)
    assert result.ok, [i.message for i in result.errors]


def test_build_lat_graph_sets_metadata(lat_md_project_root):
    graph = build_lat_graph(lat_md_project_root)
    assert graph.metadata["source"] == "lat-md"
    assert graph.metadata["source_hash"]
    assert graph.version == "lat-md-1"


def test_build_lat_graph_missing_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_lat_graph(tmp_path)


def test_split_sections_intro_and_headings():
    text = "Intro text.\n\n## First\n\nBody one.\n\n## Second\n\nBody two.\n"
    sections = split_sections(text)
    assert sections[0] == (None, "Intro text.")
    assert sections[1][0] == "First"
    assert sections[2][0] == "Second"


def test_split_sections_no_headings_returns_single_intro():
    assert split_sections("Just prose, no headings.") == [(None, "Just prose, no headings.")]


def test_split_sections_empty_text_returns_empty():
    assert split_sections("") == []


def test_compute_lat_source_hash_changes_when_file_edited(lat_md_project_root):
    original = compute_lat_source_hash(lat_md_project_root)
    auth_md = lat_md_project_root / "lat.md" / "auth.md"
    auth_md.write_text(auth_md.read_text(encoding="utf-8") + "\n## New Section\n\nMore.\n", encoding="utf-8")
    assert compute_lat_source_hash(lat_md_project_root) != original


def test_write_lat_graph_round_trips(lat_md_project_root):
    graph = build_lat_graph(lat_md_project_root)
    written = write_lat_graph(lat_md_project_root, graph)
    assert written == lat_graph_path(lat_md_project_root)
    assert written.is_file()

    data = serialize_graph(graph)
    assert data["version"] == "lat-md-1"
    assert len(data["nodes"]) == graph.node_count
    assert len(data["edges"]) == graph.edge_count


def test_write_lat_graph_custom_output_path(lat_md_project_root, tmp_path):
    graph = build_lat_graph(lat_md_project_root)
    custom_path = tmp_path / "custom" / "graph.json"
    written = write_lat_graph(lat_md_project_root, graph, custom_path)
    assert written == custom_path
    assert custom_path.is_file()
