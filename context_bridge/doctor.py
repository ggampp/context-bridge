from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from context_bridge.core.paths import ProjectPaths, resolve_project_paths
from context_bridge.core.subprocess_runner import run_command, which
from context_bridge.engram.config import load_engram_config
from context_bridge.engram.probe import probe_cli, probe_http
from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.validate import validate_graph


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str  # OK | WARN | FAIL
    detail: str

    def line(self) -> str:
        return f"  [{self.status}] {self.name}: {self.detail}"


def _check_python() -> CheckResult:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        return CheckResult("python", "OK", f"{major}.{minor} (>= 3.10 required)")
    return CheckResult("python", "FAIL", f"{major}.{minor} — Python 3.10+ required")


def _check_engram_backend() -> CheckResult:
    config = load_engram_config(timeout=2.0)
    http_status = probe_http(config)
    if http_status.available:
        return CheckResult("engram", "OK", f"HTTP backend — {http_status.detail}")

    cli_status = probe_cli()
    if cli_status.available:
        return CheckResult("engram", "OK", f"CLI fallback — {cli_status.detail}")

    return CheckResult(
        "engram",
        "WARN",
        "no backend reachable — start `engram serve` or install "
        "https://github.com/Gentleman-Programming/engram (CLI in PATH)",
    )


def _check_ua_dir(paths: ProjectPaths) -> CheckResult:
    if paths.has_ua_dir:
        return CheckResult("ua-directory", "OK", str(paths.ua_dir))
    return CheckResult(
        "ua-directory",
        "WARN",
        f"{paths.ua_dir} not found — run /understand first",
    )


def _format_age(mtime: float) -> str:
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    age_days = (datetime.now(tz=timezone.utc) - dt).days
    return f"{dt.date().isoformat()} ({age_days}d ago)"


def _git_last_commit_age(path: Path, project_root: Path) -> str | None:
    if not which("git"):
        return None
    rel = path.relative_to(project_root) if path.is_relative_to(project_root) else path.name
    result = run_command(
        ["git", "log", "-1", "--format=%ci", "--", str(rel)],
        cwd=str(project_root),
        timeout=10,
    )
    if not result.success or not result.stdout.strip():
        return None
    return result.stdout.strip()


def _check_knowledge_graph(paths: ProjectPaths) -> CheckResult:
    if not paths.has_knowledge_graph:
        return CheckResult(
            "knowledge-graph",
            "WARN",
            f"not found at {paths.knowledge_graph}",
        )

    mtime = paths.knowledge_graph.stat().st_mtime
    age = _format_age(mtime)
    git_info = _git_last_commit_age(paths.knowledge_graph, paths.project_root)
    age_detail = f"modified {age}"
    if git_info:
        age_detail += f"; last git commit {git_info}"

    try:
        graph = load_knowledge_graph(paths.project_root, use_cache=False)
    except (FileNotFoundError, ValueError) as e:
        return CheckResult("knowledge-graph", "FAIL", str(e))

    validation = validate_graph(graph)
    if not validation.ok:
        err = validation.errors[0].message if validation.errors else "validation failed"
        return CheckResult(
            "knowledge-graph",
            "FAIL",
            f"{graph.node_count} nodes, {graph.edge_count} edges — {err}",
        )

    warn_suffix = ""
    if validation.warnings:
        warn_suffix = f"; {len(validation.warnings)} warning(s)"

    status = "OK" if graph.node_count > 0 else "WARN"
    return CheckResult(
        "knowledge-graph",
        status,
        f"{graph.node_count} nodes, {graph.edge_count} edges; {age_detail}{warn_suffix}",
    )


def _check_lat_md(paths: ProjectPaths) -> CheckResult:
    lat_dir = paths.project_root / "lat.md"
    if not lat_dir.is_dir():
        return CheckResult(
            "lat-md",
            "OK",
            "not present — optional secondary source (see docs/SOURCES.md)",
        )
    md_files = sorted(lat_dir.glob("*.md"))
    return CheckResult("lat-md", "OK", f"{lat_dir} — {len(md_files)} domain file(s)")


def _check_lat_cli() -> CheckResult:
    path = which("lat")
    if path:
        return CheckResult("lat-cli", "OK", f"found at {path}")
    return CheckResult(
        "lat-cli",
        "OK",
        "not found in PATH — optional, context-bridge parses lat.md/ directly",
    )


def run_checks(project: str | Path | None = None) -> list[CheckResult]:
    paths = resolve_project_paths(project)
    return [
        _check_python(),
        _check_engram_backend(),
        _check_ua_dir(paths),
        _check_knowledge_graph(paths),
        _check_lat_md(paths),
        _check_lat_cli(),
    ]


def run_doctor(project: str | Path | None = None) -> int:
    paths = resolve_project_paths(project)
    checks = run_checks(project)

    print("")
    print("Context Bridge — Status")
    print("=" * 40)
    print(f"  Project: {paths.project_root}")
    print(f"  Engram data: {paths.engram_data_dir}")
    print("")

    for check in checks:
        print(check.line())

    ok = sum(1 for c in checks if c.status == "OK")
    warn = sum(1 for c in checks if c.status == "WARN")
    fail = sum(1 for c in checks if c.status == "FAIL")
    print("")
    print(f"Summary: {ok} OK, {warn} WARN, {fail} FAIL")
    print("")

    if fail:
        return 1
    return 0
