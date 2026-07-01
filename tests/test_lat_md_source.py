from __future__ import annotations

from context_bridge.sources.lat_md import LatMdSource, lat_graph_path
from context_bridge.sources.resolver import (
    active_source_name,
    default_graph_ref,
    graph_file_path,
    load_graph_source_config,
    resolve_graph,
)
from context_bridge.sources.ua import UASource


def test_lat_md_source_available_when_lat_dir_present(lat_md_project_root):
    assert LatMdSource().available(lat_md_project_root) is True


def test_lat_md_source_unavailable_without_lat_dir(tmp_path):
    assert LatMdSource().available(tmp_path) is False


def test_lat_md_source_load_builds_and_caches(lat_md_project_root):
    source = LatMdSource()
    graph = source.load(lat_md_project_root)
    assert graph.node_count > 0
    assert lat_graph_path(lat_md_project_root).is_file()

    # Second load reuses the cached file since the source hash is unchanged.
    cached_graph = source.load(lat_md_project_root)
    assert cached_graph.metadata["source_hash"] == graph.metadata["source_hash"]


def test_lat_md_source_rebuilds_when_stale(lat_md_project_root):
    source = LatMdSource()
    first = source.load(lat_md_project_root)

    auth_md = lat_md_project_root / "lat.md" / "auth.md"
    auth_md.write_text(auth_md.read_text(encoding="utf-8") + "\n## Extra\n\nMore.\n", encoding="utf-8")

    second = source.load(lat_md_project_root)
    assert second.node_count == first.node_count + 1


def test_ua_source_unavailable_without_knowledge_graph(tmp_path):
    assert UASource().available(tmp_path) is False


def test_ua_source_available_on_fixture(sample_project_root):
    assert UASource().available(sample_project_root) is True


def test_resolve_graph_prefers_ua_when_both_available(sample_project_root):
    (sample_project_root / "lat.md").mkdir()
    (sample_project_root / "lat.md" / "domain.md").write_text("Some domain.\n", encoding="utf-8")
    assert active_source_name(sample_project_root) == "ua"
    graph = resolve_graph(sample_project_root)
    assert graph.metadata.get("source") != "lat-md"


def test_resolve_graph_falls_back_to_lat_md(lat_md_project_root):
    assert active_source_name(lat_md_project_root) == "lat-md"
    graph = resolve_graph(lat_md_project_root)
    assert graph.metadata.get("source") == "lat-md"


def test_active_source_name_none_when_nothing_available(tmp_path):
    assert active_source_name(tmp_path) is None


def test_default_graph_ref_per_source():
    assert default_graph_ref("ua") == ".understand-anything/knowledge-graph.json"
    assert default_graph_ref("lat-md") == ".context-bridge/lat-graph.json"
    assert default_graph_ref(None) == default_graph_ref("ua")


def test_graph_file_path_per_source(lat_md_project_root):
    path = graph_file_path(lat_md_project_root, "lat-md")
    assert path == lat_graph_path(lat_md_project_root)


def test_load_graph_source_config_reads_priority(tmp_path):
    config_file = tmp_path / "graph-source.yaml"
    config_file.write_text("priority:\n  - lat-md\n  - ua\n", encoding="utf-8")
    config = load_graph_source_config(config_file)
    assert config.priority == ("lat-md", "ua")


def test_load_graph_source_config_defaults_when_missing(tmp_path):
    config = load_graph_source_config(tmp_path / "missing.yaml")
    assert config.priority == ("ua", "lat-md")
