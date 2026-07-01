from __future__ import annotations

from context_bridge.sources.lat_md.annotations import scan_annotations


def test_scan_annotations_finds_lat_comment(lat_md_project_root):
    annotations = scan_annotations(lat_md_project_root)
    assert len(annotations) == 1
    annotation = annotations[0]
    assert annotation.file_path == "src/auth.ts"
    assert annotation.line == 1
    assert annotation.link.target == "auth"
    assert annotation.link.section == "OAuth Flow"


def test_scan_annotations_ignores_skip_dirs(tmp_path):
    node_modules = tmp_path / "node_modules" / "pkg"
    node_modules.mkdir(parents=True)
    (node_modules / "index.js").write_text("// @lat: [[auth#OAuth Flow]]\n", encoding="utf-8")
    assert scan_annotations(tmp_path) == []


def test_scan_annotations_empty_for_no_matches(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "plain.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    assert scan_annotations(tmp_path) == []
