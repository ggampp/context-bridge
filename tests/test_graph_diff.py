from __future__ import annotations

import json

from context_bridge.graph.diff import load_diff_overlay


def test_load_diff_overlay_missing(sample_project_root):
    assert load_diff_overlay(sample_project_root) is None


def test_load_diff_overlay_parses(sample_project_root):
    overlay = sample_project_root / ".understand-anything" / "diff-overlay.json"
    overlay.write_text(
        json.dumps(
            {
                "changedPaths": ["src/auth/login.ts"],
                "addedNodeIds": ["node-new"],
            }
        ),
        encoding="utf-8",
    )
    diff = load_diff_overlay(sample_project_root)
    assert diff is not None
    assert diff.has_changes
    assert "src/auth/login.ts" in diff.changed_paths
    assert "node-new" in diff.added_node_ids
