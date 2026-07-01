from __future__ import annotations

import re
from dataclasses import dataclass

from context_bridge.sources.lat_md.wiki_links import WikiLink, is_code_ref

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-") or "item"


@dataclass(frozen=True)
class CodeRef:
    path: str
    symbol: str | None  # function/class/etc name, when the link targets a symbol


def parse_code_ref(link: WikiLink) -> CodeRef | None:
    """Turn a wiki link like `[[src/auth.ts#validateToken]]` into a CodeRef.

    Returns None for links that aren't code references (see `is_code_ref`).
    """
    if not is_code_ref(link):
        return None
    return CodeRef(path=link.target, symbol=link.section)


def code_ref_node_id(ref: CodeRef) -> str:
    """Stable graph node id for a code reference, e.g. `lat-code-src-auth-ts-validatetoken`."""
    path_slug = _slugify(ref.path)
    if ref.symbol:
        return f"lat-code-{path_slug}-{_slugify(ref.symbol)}"
    return f"lat-code-{path_slug}"
