from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SyncItemResult:
    topic_key: str
    title: str
    type: str
    status: str  # would-create | would-update | would-skip | created | updated | skipped | error
    observation_id: int | str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_key": self.topic_key,
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "observation_id": self.observation_id,
            "error": self.error,
        }


@dataclass
class SyncReport:
    items: list[SyncItemResult] = field(default_factory=list)
    graph_skipped: bool = False
    backend: str | None = None
    graph_age_days: float | None = None
    duration_seconds: float | None = None

    @property
    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.status] = counts.get(item.status, 0) + 1
        return counts

    @property
    def counts_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.type] = counts.get(item.type, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_skipped": self.graph_skipped,
            "backend": self.backend,
            "graph_age_days": self.graph_age_days,
            "duration_seconds": self.duration_seconds,
            "counts": self.counts,
            "counts_by_type": self.counts_by_type,
            "items": [i.to_dict() for i in self.items],
        }


def _format_metrics_line(report: SyncReport) -> str | None:
    parts = []
    if report.graph_age_days is not None:
        parts.append(f"graph age: {report.graph_age_days:.1f}d")
    if report.duration_seconds is not None:
        parts.append(f"duration: {report.duration_seconds:.2f}s")
    if not parts:
        return None
    return "  " + " | ".join(parts)


def format_report(report: SyncReport, *, verbose: bool = False) -> str:
    lines = ["", "Sync Report", "=" * 40]
    metrics_line = _format_metrics_line(report)
    if report.graph_skipped:
        lines.append("  Graph unchanged since last sync — nothing to do.")
        if metrics_line:
            lines.append(metrics_line)
        lines.append("")
        return "\n".join(lines)

    if report.backend:
        lines.append(f"  Backend: {report.backend}")
    if metrics_line:
        lines.append(metrics_line)
    lines.append("")
    lines.append("By status:")
    for status, count in sorted(report.counts.items()):
        lines.append(f"  {status}: {count}")
    lines.append("")
    lines.append("By type:")
    for type_, count in sorted(report.counts_by_type.items()):
        lines.append(f"  {type_}: {count}")
    if verbose:
        lines.append("")
        for item in report.items:
            suffix = f" (id={item.observation_id})" if item.observation_id else ""
            err = f" — ERROR: {item.error}" if item.error else ""
            lines.append(f"  [{item.status}] {item.type}: {item.title}{suffix}{err}")
    lines.append("")
    return "\n".join(lines)
