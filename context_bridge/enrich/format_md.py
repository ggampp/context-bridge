from __future__ import annotations

from context_bridge.enrich.pipeline import EnrichResult


def format_markdown(result: EnrichResult) -> str:
    lines = [f'## Enrich: "{result.query}"', ""]

    lines.append(f"### Memórias Engram ({len(result.memories)})")
    if not result.memories:
        lines.append("_Nenhuma memória encontrada para esta busca._")
    for i, em in enumerate(result.memories, start=1):
        title = em.memory.get("title") or em.memory.get("topic_key") or "(sem título)"
        lines.append(f"{i}. **{title}**")
        nodes = em.graph_context.all_nodes
        if nodes:
            paths = ", ".join(f"`{n.path or n.id}`" for n in nodes[:5])
            lines.append(f"   - Graph: {paths}")
        elif em.graph_context.note:
            lines.append(f"   - Graph: _{em.graph_context.note}_")
    lines.append("")

    graph_nodes = result.graph_nodes
    if graph_nodes:
        lines.append("### Contexto do grafo (relacionado)")
        lines.append("| Nó | Camada | Resumo |")
        lines.append("|----|--------|--------|")
        for node in graph_nodes:
            summary = (node.summary or "").replace("|", "/")[:80]
            lines.append(f"| {node.path or node.id} | {node.layer or '—'} | {summary or '—'} |")
        lines.append("")
    elif not result.graph_available:
        lines.append("_Grafo Understand Anything indisponível neste projeto — apenas memórias retornadas._")
        lines.append("")

    return "\n".join(lines)
