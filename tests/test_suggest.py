from __future__ import annotations

from context_bridge.suggest import build_suggestions


def test_build_suggestions_returns_payloads(sample_project_root):
    payloads = build_suggestions(sample_project_root)
    assert payloads
    for p in payloads:
        d = p.to_dict()
        assert {"title", "type", "topic_key", "content", "project", "scope"} <= d.keys()
        assert d["topic_key"].startswith("cb-")


def test_build_suggestions_respects_types_filter(sample_project_root):
    payloads = build_suggestions(sample_project_root, types={"architecture"})
    assert payloads
    assert all(p.type == "architecture" for p in payloads)


def test_build_suggestions_missing_graph_raises(tmp_path):
    try:
        build_suggestions(tmp_path)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_build_suggestions_has_no_side_effects(sample_project_root):
    build_suggestions(sample_project_root)
    assert not (sample_project_root / ".context-bridge").exists()
