from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from context_bridge.core.subprocess_runner import which

_MCP_SERVER_KEY = "context-bridge"


@dataclass
class InstallAction:
    description: str
    command: list[str] | None = None
    target_path: Path | None = None
    executed: bool = False
    skipped: bool = False
    reason: str = ""


@dataclass
class InstallReport:
    env: str
    dry_run: bool
    force: bool
    project_root: Path
    actions: list[InstallAction] = field(default_factory=list)

    def add(
        self,
        description: str,
        command: list[str] | None = None,
        *,
        target_path: Path | None = None,
    ) -> None:
        self.actions.append(InstallAction(description=description, command=command, target_path=target_path))


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _mcp_config_path(env: str, project_root: Path) -> Path | None:
    if env in {"cursor", "auto"}:
        return project_root / ".cursor" / "mcp.json"
    return None


def build_install_report(
    *,
    env: str = "auto",
    dry_run: bool = False,
    force: bool = False,
    project: str | Path | None = None,
) -> InstallReport:
    project_root = Path(project or Path.cwd()).resolve()
    report = InstallReport(env=env, dry_run=dry_run, force=force, project_root=project_root)

    if not _has_module("mcp"):
        report.add(
            "Install MCP SDK for the context-bridge MCP server",
            [sys.executable, "-m", "pip", "install", "context-bridge[mcp]"],
        )

    if not which("engram"):
        report.add(
            "Install Engram (optional, enables CLI fallback): "
            "https://github.com/Gentleman-Programming/engram",
            None,
        )

    config_path = _mcp_config_path(env, project_root)
    if config_path is not None:
        report.add(f"Write MCP server config to {config_path}", None, target_path=config_path)

    return report


def _write_mcp_config(path: Path, *, force: bool) -> tuple[bool, str]:
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict = {}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}

    servers = existing.setdefault("mcpServers", {})
    if _MCP_SERVER_KEY in servers and not force:
        return False, "already configured (use --force to overwrite)"

    servers[_MCP_SERVER_KEY] = {"command": "context-bridge", "args": ["mcp"]}
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True, ""


def execute_install_report(report: InstallReport) -> InstallReport:
    for action in report.actions:
        if report.dry_run:
            action.skipped = True
            action.reason = "dry-run"
            continue

        if action.target_path is not None:
            try:
                wrote, reason = _write_mcp_config(action.target_path, force=report.force)
            except OSError as e:
                action.skipped = True
                action.reason = str(e)
                continue
            action.executed = wrote
            action.skipped = not wrote
            action.reason = reason
            continue

        if action.command is None:
            action.skipped = True
            action.reason = "manual step"
            continue

        try:
            result = subprocess.run(action.command, capture_output=True, text=True, check=False, timeout=120)
            action.executed = result.returncode == 0
            if not action.executed:
                action.reason = (result.stderr or result.stdout or "failed").strip()[:200]
        except (OSError, subprocess.TimeoutExpired) as e:
            action.skipped = True
            action.reason = str(e)

    return report
