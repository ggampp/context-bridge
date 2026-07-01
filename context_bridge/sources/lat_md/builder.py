from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from context_bridge.graph.models import GraphEdge, GraphNode, KnowledgeGraph
from context_bridge.sources.lat_md.annotations import scan_annotations
from context_bridge.sources.lat_md.code_refs import code_ref_node_id, parse_code_ref
from context_bridge.sources.lat_md.wiki_links import parse_wiki_links

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-") or "item"


def lat_graph_path(project_root: str | Path) -> Path:
    return Path(project_root) / ".context-bridge" / "lat-graph.json"


def _lat_md_dir(project_root: str | Path) -> Path:
    return Path(project_root) / "lat.md"


def split_sections(text: str) -> list[tuple[str | None, str]]:
    """Split a lat.md file into `(title, body)` pairs on `## Heading` lines.

    The leading chunk before the first `##` (if any) is returned with
    `title=None` and used as the domain-level summary.
    """
    matches = list(_SECTION_RE.finditer(text))
    if not matches:
        stripped = text.strip()
        return [(None, stripped)] if stripped else []

    sections: list[tuple[str | None, str]] = []
    intro = text[: matches[0].start()].strip()
    if intro:
        sections.append((None, intro))

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((title, text[start:end].strip()))

    return sections


def compute_lat_source_hash(project_root: str | Path) -> str:
    """Fingerprint of `lat.md/*.md` + any file carrying an `@lat:` annotation.

    Used by `LatMdSource` to skip rebuilding `.context-bridge/lat-graph.json`
    when nothing relevant changed since the last build.
    """
    root = Path(project_root)
    lat_dir = _lat_md_dir(root)
    entries: list[str] = []

    if lat_dir.is_dir():
        for md_file in sorted(lat_dir.rglob("*.md")):
            stat = md_file.stat()
            entries.append(f"{md_file.relative_to(root).as_posix()}:{stat.st_mtime_ns}:{stat.st_size}")

    annotated_files = sorted({a.file_path for a in scan_annotations(root)})
    for rel in annotated_files:
        path = root / rel
        if path.is_file():
            stat = path.stat()
            entries.append(f"{rel}:{stat.st_mtime_ns}:{stat.st_size}")

    return hashlib.sha256("|".join(entries).encode("utf-8")).hexdigest()


def build_lat_graph(project_root: str | Path) -> KnowledgeGraph:
    """Parse `lat.md/*.md` (+ `@lat:` annotations in source files) into a KnowledgeGraph.

    Node types: `domain` (one per lat.md/*.md file), `concept` (one per `##`
    section), `file`/`function` (code referenced via wiki links or
    annotations). Edge types: `contains` (domain->concept), `relates_to`
    (concept->concept wiki links), `references` (concept<->code).
    """
    root = Path(project_root)
    lat_dir = _lat_md_dir(root)
    if not lat_dir.is_dir():
        raise FileNotFoundError(
            f"lat.md directory not found at {lat_dir}. "
            "Create lat.md/<domain>.md files first (see docs/SOURCES.md)."
        )

    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    for md_file in sorted(lat_dir.glob("*.md")):
        domain_slug = _slugify(md_file.stem)
        domain_id = f"lat-{domain_slug}"
        text = md_file.read_text(encoding="utf-8")
        sections = split_sections(text)
        rel_path = md_file.relative_to(root).as_posix()

        intro = next((body for title, body in sections if title is None), "")
        nodes[domain_id] = GraphNode(
            id=domain_id,
            label=md_file.stem,
            type="domain",
            path=rel_path,
            domain=domain_slug,
            summary=intro[:500],
        )

        for title, body in sections:
            if title is None:
                continue
            concept_id = f"lat-{domain_slug}-{_slugify(title)}"
            nodes[concept_id] = GraphNode(
                id=concept_id,
                label=title,
                type="concept",
                path=rel_path,
                domain=domain_slug,
                summary=body[:500],
            )
            edges.append(GraphEdge(source=domain_id, target=concept_id, type="contains"))

            for link in parse_wiki_links(body):
                code_ref = parse_code_ref(link)
                if code_ref is not None:
                    code_id = code_ref_node_id(code_ref)
                    nodes.setdefault(
                        code_id,
                        GraphNode(
                            id=code_id,
                            label=code_ref.symbol or Path(code_ref.path).name,
                            type="function" if code_ref.symbol else "file",
                            path=code_ref.path,
                        ),
                    )
                    edges.append(GraphEdge(source=concept_id, target=code_id, type="references"))
                    continue

                target_domain_slug = _slugify(link.target) if link.target else domain_slug
                target_id = (
                    f"lat-{target_domain_slug}-{_slugify(link.section)}"
                    if link.section
                    else f"lat-{target_domain_slug}"
                )
                if target_id != concept_id:
                    edges.append(GraphEdge(source=concept_id, target=target_id, type="relates_to"))

    for annotation in scan_annotations(root):
        link = annotation.link
        if not link.target:
            continue  # same-file section ref makes no sense from outside lat.md
        code_id = f"lat-code-{_slugify(annotation.file_path)}"
        nodes.setdefault(
            code_id,
            GraphNode(
                id=code_id,
                label=Path(annotation.file_path).name,
                type="file",
                path=annotation.file_path,
            ),
        )
        target_domain_slug = _slugify(link.target)
        target_id = (
            f"lat-{target_domain_slug}-{_slugify(link.section)}" if link.section else f"lat-{target_domain_slug}"
        )
        if target_id in nodes:
            edges.append(GraphEdge(source=code_id, target=target_id, type="references"))

    seen: set[tuple[str, str, str]] = set()
    unique_edges: list[GraphEdge] = []
    for edge in edges:
        key = (edge.source, edge.target, edge.type)
        if key in seen:
            continue
        seen.add(key)
        unique_edges.append(edge)

    return KnowledgeGraph(
        version="lat-md-1",
        nodes=list(nodes.values()),
        edges=unique_edges,
        metadata={
            "source": "lat-md",
            "source_hash": compute_lat_source_hash(root),
            "built_at": datetime.now(tz=timezone.utc).isoformat(),
        },
        source_path=str(lat_dir),
    )


def _node_to_dict(node: GraphNode) -> dict:
    data = {
        "id": node.id,
        "label": node.label,
        "type": node.type,
        "path": node.path,
        "layer": node.layer,
        "summary": node.summary,
        "domain": node.domain,
        "language": node.language,
    }
    data = {k: v for k, v in data.items() if v}
    data["id"] = node.id
    data.update(node.extra)
    return data


def _edge_to_dict(edge: GraphEdge) -> dict:
    data = {"source": edge.source, "target": edge.target, "type": edge.type}
    data.update(edge.extra)
    return data


def serialize_graph(graph: KnowledgeGraph) -> dict:
    return {
        "version": graph.version,
        "metadata": graph.metadata,
        "nodes": [_node_to_dict(n) for n in graph.nodes],
        "edges": [_edge_to_dict(e) for e in graph.edges],
    }


def write_lat_graph(
    project_root: str | Path,
    graph: KnowledgeGraph,
    output_path: str | Path | None = None,
) -> Path:
    path = Path(output_path) if output_path else lat_graph_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialize_graph(graph), indent=2, ensure_ascii=False), encoding="utf-8")
    return path
