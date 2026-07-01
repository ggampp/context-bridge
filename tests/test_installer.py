from __future__ import annotations

import json

from context_bridge.core.installer import build_install_report, execute_install_report


def test_build_install_report_includes_mcp_config_action(tmp_path):
    report = build_install_report(env="cursor", project=tmp_path)
    targets = [a.target_path for a in report.actions if a.target_path]
    assert tmp_path / ".cursor" / "mcp.json" in targets


def test_dry_run_skips_all_actions(tmp_path):
    report = build_install_report(env="cursor", dry_run=True, project=tmp_path)
    report = execute_install_report(report)
    assert report.actions
    for action in report.actions:
        assert action.skipped
        assert action.reason == "dry-run"
        assert not action.executed
    assert not (tmp_path / ".cursor" / "mcp.json").exists()


def test_execute_writes_mcp_config(tmp_path):
    report = build_install_report(env="cursor", project=tmp_path)
    report = execute_install_report(report)

    config_path = tmp_path / ".cursor" / "mcp.json"
    assert config_path.is_file()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["mcpServers"]["context-bridge"] == {"command": "context-bridge", "args": ["mcp"]}


def test_execute_does_not_overwrite_without_force(tmp_path):
    config_path = tmp_path / ".cursor" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"mcpServers": {"context-bridge": {"command": "custom"}}}),
        encoding="utf-8",
    )

    report = build_install_report(env="cursor", project=tmp_path)
    report = execute_install_report(report)

    mcp_action = next(a for a in report.actions if a.target_path == config_path)
    assert mcp_action.skipped
    assert "already configured" in mcp_action.reason

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["mcpServers"]["context-bridge"] == {"command": "custom"}


def test_execute_overwrites_with_force(tmp_path):
    config_path = tmp_path / ".cursor" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"mcpServers": {"context-bridge": {"command": "custom"}}}),
        encoding="utf-8",
    )

    report = build_install_report(env="cursor", force=True, project=tmp_path)
    report = execute_install_report(report)

    mcp_action = next(a for a in report.actions if a.target_path == config_path)
    assert mcp_action.executed

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["mcpServers"]["context-bridge"] == {"command": "context-bridge", "args": ["mcp"]}


def test_execute_preserves_other_mcp_servers(tmp_path):
    config_path = tmp_path / ".cursor" / "mcp.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"mcpServers": {"other-tool": {"command": "other"}}}),
        encoding="utf-8",
    )

    report = build_install_report(env="cursor", project=tmp_path)
    execute_install_report(report)

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert "other-tool" in data["mcpServers"]
    assert "context-bridge" in data["mcpServers"]


def test_env_none_skips_mcp_config_action(tmp_path):
    report = build_install_report(env="none", project=tmp_path)
    assert all(a.target_path is None for a in report.actions)
