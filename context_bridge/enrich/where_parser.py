from __future__ import annotations

import re
from dataclasses import dataclass

# Matches the structured **Where**: line written by context-bridge's own
# MemSavePayload.content format (see engram/payloads.py), and tolerates the
# same field in manually-written Engram memories that follow the documented
# Memory Protocol (`**Where**: ...`).
_WHERE_LINE_RE = re.compile(r"\*\*Where\*\*:\s*(?P<value>.+)")

# context-bridge anchors generated during sync, e.g.:
#   .understand-anything/knowledge-graph.json#layer:api
#   .understand-anything/knowledge-graph.json#node:node-router (src/api/router.ts)
#   .understand-anything/knowledge-graph.json#domain:auth
_ANCHOR_RE = re.compile(r"#(?P<kind>layer|node|domain|tours):?(?P<value>[^\s(]*)\s*(?:\((?P<extra>[^)]+)\))?")

# Loose heuristic for bare file paths in manually-written memories, e.g.
# "src/auth/login.ts, src/auth/middleware.ts".
_PATH_TOKEN_RE = re.compile(r"[\w./-]+\.[A-Za-z0-9]{1,5}")


@dataclass(frozen=True)
class ParsedWhere:
    kind: str  # layer | node | domain | tours | path | unknown
    value: str
    paths: tuple[str, ...] = ()

    @property
    def is_empty(self) -> bool:
        return self.kind == "unknown" and not self.paths


def extract_where_line(content: str) -> str | None:
    """Pull the `**Where**: ...` value out of an observation's content body."""
    if not content:
        return None
    match = _WHERE_LINE_RE.search(content)
    if not match:
        return None
    value = match.group("value").strip()
    # Stop at the next markdown bold marker (e.g. "**Learned**:") if present.
    next_marker = value.find("**")
    if next_marker != -1:
        value = value[:next_marker].strip()
    return value or None


def parse_where(where: str) -> ParsedWhere:
    """Interpret a `where` value into a graph lookup hint.

    Recognizes context-bridge's own anchors first (#layer/#node/#domain),
    then falls back to extracting bare file paths for manually-written
    memories.
    """
    if not where:
        return ParsedWhere(kind="unknown", value="")

    anchor = _ANCHOR_RE.search(where)
    if anchor:
        kind = anchor.group("kind")
        value = anchor.group("value") or ""
        extra = anchor.group("extra")
        paths = (extra,) if extra else ()
        if kind == "tours":
            return ParsedWhere(kind="tours", value="", paths=paths)
        return ParsedWhere(kind=kind, value=value, paths=paths)

    paths = tuple(dict.fromkeys(_PATH_TOKEN_RE.findall(where)))
    if paths:
        return ParsedWhere(kind="path", value=where, paths=paths)

    return ParsedWhere(kind="unknown", value=where)
