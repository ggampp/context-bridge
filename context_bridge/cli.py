from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from context_bridge import __version__
from context_bridge.core.paths import resolve_project_paths
from context_bridge.doctor import run_doctor
from context_bridge.engram.errors import EngramError
from context_bridge.enrich.format_json import format_json_dict
from context_bridge.enrich.format_md import format_markdown
from context_bridge.enrich.pipeline import run_enrich
from context_bridge.graph.diff import load_diff_overlay
from context_bridge.graph.loader import load_knowledge_graph
from context_bridge.graph.queries import find_node, graph_languages, hub_nodes, nodes_by_domain, nodes_by_layer
from context_bridge.graph.validate import validate_graph
from context_bridge.core.installer import build_install_report, execute_install_report
from context_bridge.hooks.post_sync import render_post_enrich_note, render_post_sync_note
from context_bridge.sources.lat_md import build_lat_graph, lat_graph_path, write_lat_graph
from context_bridge.suggest import build_suggestions
from context_bridge.sync.engine import run_sync
from context_bridge.sync.report import format_report


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _add_project_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        "-p",
        default=".",
        help="Project root containing .understand-anything/ (default: cwd)",
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    return run_doctor(args.project)


def cmd_sync(args: argparse.Namespace) -> int:
    types = {t.strip() for t in args.types.split(",")} if args.types else None
    try:
        report = run_sync(
            args.project,
            dry_run=args.dry_run,
            incremental=args.incremental,
            force=args.force,
            types=types,
        )
    except (FileNotFoundError, ValueError, EngramError) as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        _print_json(report.to_dict())
    else:
        print(format_report(report, verbose=args.verbose))
        if not args.quiet:
            print(render_post_sync_note(report))

    return 1 if report.counts.get("error") else 0


def cmd_enrich(args: argparse.Namespace) -> int:
    try:
        result = run_enrich(
            args.project,
            args.query,
            limit=args.limit,
            hops=args.hops,
            node_limit=args.node_limit,
        )
    except EngramError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        _print_json(format_json_dict(result))
    else:
        print(format_markdown(result))
        if not args.quiet:
            note = render_post_enrich_note(result)
            if note:
                print(note)

    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    types = {t.strip() for t in args.types.split(",")} if args.types else None
    try:
        payloads = build_suggestions(args.project, types=types)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        _print_json([p.to_dict() for p in payloads])
        return 0

    print("")
    print(f"Suggested memories ({len(payloads)})")
    print("=" * 40)
    for p in payloads:
        print(f"  [{p.type}] {p.title}  (topic_key={p.topic_key})")
    print("")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    report = build_install_report(env=args.env, dry_run=args.dry_run, force=args.force, project=args.project)
    report = execute_install_report(report)

    print("")
    print(f"Install plan (env={args.env}, dry_run={args.dry_run}, force={args.force})")
    for action in report.actions:
        status = "EXEC" if action.executed else ("SKIP" if action.skipped else "PLAN")
        target = str(action.target_path) if action.target_path else " ".join(action.command or []) or "(manual)"
        print(f"  [{status}] {action.description}")
        print(f"         {target}")
        if action.reason:
            print(f"         reason: {action.reason}")
    print("")

    if not args.dry_run:
        print("Run: context-bridge doctor")
    return 0


def cmd_mcp(_: argparse.Namespace) -> int:
    from context_bridge.mcp_server import run_mcp

    return run_mcp()


def cmd_graph_stats(args: argparse.Namespace) -> int:
    try:
        graph = load_knowledge_graph(args.project)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1

    layers = nodes_by_layer(graph)
    hubs = hub_nodes(graph, min_degree=args.min_degree, limit=args.hub_limit)
    domains = nodes_by_domain(graph)
    languages = graph_languages(graph)
    diff = load_diff_overlay(args.project)

    if args.json:
        _print_json(
            {
                "version": graph.version,
                "source": graph.source_path,
                "nodes": graph.node_count,
                "edges": graph.edge_count,
                "layers": {k: len(v) for k, v in layers.items()},
                "domains": {k: len(v) for k, v in domains.items()},
                "languages": languages,
                "top_hubs": [
                    {
                        "id": h.node.id,
                        "label": h.node.label,
                        "path": h.node.path,
                        "degree": h.degree,
                    }
                    for h in hubs
                ],
                "diff_overlay": {
                    "present": diff is not None,
                    "has_changes": diff.has_changes if diff else False,
                },
            }
        )
        return 0

    print("")
    print("Knowledge Graph — Stats")
    print("=" * 40)
    print(f"  Source: {graph.source_path}")
    print(f"  Version: {graph.version or '(unset)'}")
    print(f"  Nodes: {graph.node_count}")
    print(f"  Edges: {graph.edge_count}")
    print("")
    print("Layers:")
    for layer, nodes in layers.items():
        print(f"  {layer}: {len(nodes)}")
    if languages:
        print("")
        print("Languages:")
        for lang, count in languages.items():
            print(f"  {lang}: {count}")
    if domains:
        print("")
        print("Domains:")
        for domain, nodes in domains.items():
            print(f"  {domain}: {len(nodes)}")
    if hubs:
        print("")
        print(f"Top hubs (degree >= {args.min_degree}):")
        for h in hubs:
            label = h.node.label or h.node.id
            path = f" ({h.node.path})" if h.node.path else ""
            print(f"  [{h.degree}] {label}{path}")
    if diff:
        print("")
        status = "has pending changes" if diff.has_changes else "no pending changes"
        print(f"Diff overlay: {status}")
    print("")
    return 0


def cmd_graph_node(args: argparse.Namespace) -> int:
    try:
        graph = load_knowledge_graph(args.project)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1

    node = find_node(graph, args.identifier)
    if not node:
        print(f"Node not found: {args.identifier}", file=sys.stderr)
        return 1

    if args.json:
        _print_json(
            {
                "id": node.id,
                "label": node.label,
                "type": node.type,
                "path": node.path,
                "layer": node.layer,
                "summary": node.summary,
                "domain": node.domain,
                "language": node.language,
            }
        )
        return 0

    print("")
    print(f"Node: {node.label or node.id}")
    print("=" * 40)
    print(f"  id: {node.id}")
    if node.type:
        print(f"  type: {node.type}")
    if node.path:
        print(f"  path: {node.path}")
    if node.layer:
        print(f"  layer: {node.layer}")
    if node.domain:
        print(f"  domain: {node.domain}")
    if node.language:
        print(f"  language: {node.language}")
    if node.summary:
        print(f"  summary: {node.summary}")
    print("")
    return 0


def cmd_graph_import(args: argparse.Namespace) -> int:
    project_root = Path(args.project).resolve()
    try:
        graph = build_lat_graph(project_root)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    validation = validate_graph(graph)
    if not validation.ok:
        errors = "; ".join(issue.message for issue in validation.errors)
        print(f"Graph validation failed: {errors}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"lat.md graph (dry-run): {graph.node_count} nodes, {graph.edge_count} edges — not written")
        return 0

    output_path = Path(args.write) if args.write else lat_graph_path(project_root)
    if not output_path.is_absolute():
        output_path = project_root / output_path
    written = write_lat_graph(project_root, graph, output_path)
    print(f"Wrote {written} ({graph.node_count} nodes, {graph.edge_count} edges)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context-bridge",
        description="Bridge Understand Anything knowledge graphs to Engram memory",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_doctor = sub.add_parser("doctor", help="Check Engram and UA graph prerequisites")
    _add_project_arg(p_doctor)
    p_doctor.set_defaults(func=cmd_doctor)

    p_sync = sub.add_parser("sync", help="Sync UA graph to Engram")
    _add_project_arg(p_sync)
    p_sync.add_argument("--dry-run", action="store_true", help="List payloads without saving")
    p_sync.add_argument("--incremental", action="store_true", help="Skip sync if graph is unchanged")
    p_sync.add_argument("--force", action="store_true", help="Ignore local sync state, reprocess everything")
    p_sync.add_argument("--types", help="Comma-separated mapper types: architecture,codebase-map,domain,tour")
    p_sync.add_argument("--json", action="store_true", help="Output JSON")
    p_sync.add_argument("--verbose", action="store_true", help="List every synced item")
    p_sync.add_argument("--quiet", action="store_true", help="Suppress the Context Bridge follow-up note")
    p_sync.set_defaults(func=cmd_sync)

    p_enrich = sub.add_parser("enrich", help="Search Engram memories enriched with UA graph context")
    _add_project_arg(p_enrich)
    p_enrich.add_argument("query", help="Search query")
    p_enrich.add_argument("--json", action="store_true", help="Output JSON")
    p_enrich.add_argument("--limit", type=int, default=10, help="Max Engram memories to fetch")
    p_enrich.add_argument("--hops", type=int, default=1, help="Graph neighbor hops from each anchor node")
    p_enrich.add_argument("--node-limit", type=int, default=15, help="Max graph nodes to include")
    p_enrich.add_argument("--quiet", action="store_true", help="Suppress the Context Bridge follow-up note")
    p_enrich.set_defaults(func=cmd_enrich)

    p_suggest = sub.add_parser("suggest", help="Preview mem_save payloads from the graph (no writes)")
    _add_project_arg(p_suggest)
    p_suggest.add_argument("--types", help="Comma-separated mapper types: architecture,codebase-map,domain,tour")
    p_suggest.add_argument("--json", action="store_true", help="Output JSON")
    p_suggest.set_defaults(func=cmd_suggest)

    p_install = sub.add_parser("install", help="Install MCP config (and check optional deps)")
    _add_project_arg(p_install)
    p_install.add_argument("--env", default="auto", choices=["auto", "cursor", "none"], help="Target environment")
    p_install.add_argument("--dry-run", action="store_true", help="Show the install plan without applying it")
    p_install.add_argument("--force", action="store_true", help="Overwrite existing MCP config entry")
    p_install.set_defaults(func=cmd_install)

    p_mcp = sub.add_parser("mcp", help="Start the MCP server (stdio)")
    p_mcp.set_defaults(func=cmd_mcp)

    p_graph = sub.add_parser("graph", help="Query Understand Anything knowledge graph")
    graph_sub = p_graph.add_subparsers(dest="graph_action", required=True)

    p_stats = graph_sub.add_parser("stats", help="Graph summary statistics")
    _add_project_arg(p_stats)
    p_stats.add_argument("--json", action="store_true", help="Output JSON")
    p_stats.add_argument("--min-degree", type=int, default=5, help="Min degree for hub nodes")
    p_stats.add_argument("--hub-limit", type=int, default=10, help="Max hub nodes to list")
    p_stats.set_defaults(func=cmd_graph_stats)

    p_node = graph_sub.add_parser("node", help="Show details for a node id or file path")
    _add_project_arg(p_node)
    p_node.add_argument("identifier", help="Node id or file path")
    p_node.add_argument("--json", action="store_true", help="Output JSON")
    p_node.set_defaults(func=cmd_graph_node)

    p_import = graph_sub.add_parser("import", help="Build a KnowledgeGraph from a secondary source")
    p_import.add_argument("source", choices=["lat-md"], help="Graph source to import from")
    _add_project_arg(p_import)
    p_import.add_argument("--dry-run", action="store_true", help="Build and validate without writing")
    p_import.add_argument("--write", help="Output path (default: .context-bridge/lat-graph.json)")
    p_import.set_defaults(func=cmd_graph_import)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
