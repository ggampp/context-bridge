from __future__ import annotations

import re
from dataclasses import dataclass

# [[Target]] | [[Target#Section]] | [[Target#Section|Display text]] | [[#Section]] (same-file)
_WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#([^\]|]+))?(?:\|[^\]]+)?\]\]")

# lat.md links into source code look like a path: they contain a "/" or end
# in a recognizable code extension. Everything else is treated as a link
# between lat.md domains/sections.
_CODE_EXT_RE = re.compile(
    r"\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|cs|cpp|cc|c|h|hpp|php|swift|scala)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class WikiLink:
    target: str  # "" when the link is a same-file section ref, e.g. [[#Section]]
    section: str | None
    raw: str


def parse_wiki_links(text: str) -> list[WikiLink]:
    """Extract all `[[Target#Section]]`-style wiki links from lat.md prose."""
    links: list[WikiLink] = []
    for match in _WIKI_LINK_RE.finditer(text):
        target = match.group(1).strip()
        section = match.group(2).strip() if match.group(2) else None
        if not target and not section:
            continue
        links.append(WikiLink(target=target, section=section, raw=match.group(0)))
    return links


def is_code_ref(link: WikiLink) -> bool:
    """True when `link.target` looks like a source file path, not a lat.md domain."""
    return bool(link.target) and ("/" in link.target or bool(_CODE_EXT_RE.search(link.target)))
