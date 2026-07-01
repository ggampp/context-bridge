from __future__ import annotations

from dataclasses import dataclass, field

from context_bridge.graph.models import KnowledgeGraph


@dataclass
class ValidationIssue:
    level: str  # error | warning
    message: str


@dataclass
class ValidationResult:
    ok: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.level == "warning"]


def validate_graph(graph: KnowledgeGraph) -> ValidationResult:
    issues: list[ValidationIssue] = []

    if not graph.version:
        issues.append(ValidationIssue("warning", "Missing 'version' field in knowledge graph"))

    if not graph.nodes:
        issues.append(ValidationIssue("error", "Graph has no nodes"))

    node_ids = {n.id for n in graph.nodes}
    if len(node_ids) != len(graph.nodes):
        issues.append(ValidationIssue("error", "Duplicate node ids detected"))

    for node in graph.nodes:
        if not node.id:
            issues.append(ValidationIssue("error", "Node with empty id"))
        if node.type == "file" and not node.path:
            issues.append(
                ValidationIssue("warning", f"File node {node.id!r} has no path")
            )

    for i, edge in enumerate(graph.edges):
        if edge.source not in node_ids:
            issues.append(
                ValidationIssue("warning", f"edges[{i}] source {edge.source!r} not in nodes")
            )
        if edge.target not in node_ids:
            issues.append(
                ValidationIssue("warning", f"edges[{i}] target {edge.target!r} not in nodes")
            )

    ok = not any(i.level == "error" for i in issues)
    return ValidationResult(ok=ok, issues=issues)
