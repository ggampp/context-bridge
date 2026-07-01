from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_DEFAULT_PREFIX = "cb-"
_MAX_TOPIC_KEY_LEN = 64
_MAX_WHAT_LEN = 500


def _slugify(text: str) -> str:
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return slug or "item"


def topic_key_from_parts(*parts: str, prefix: str = _DEFAULT_PREFIX, max_len: int = _MAX_TOPIC_KEY_LEN) -> str:
    """Build a deterministic, ASCII-safe topic_key from one or more parts.

    Stable across runs for the same input — used to dedupe and upsert
    context-bridge generated memories without colliding with manual ones.
    """
    slug = "-".join(_slugify(p) for p in parts if p)
    key = f"{prefix}{slug}"
    if len(key) <= max_len:
        return key
    # Truncate but keep a short content hash suffix for stability/uniqueness.
    digest = hashlib.sha1("-".join(parts).encode("utf-8")).hexdigest()[:8]
    budget = max_len - len(prefix) - len(digest) - 1
    return f"{prefix}{slug[:budget]}-{digest}"


@dataclass(frozen=True)
class MemSavePayload:
    """Mirrors the Engram `mem_save` contract (title/type/topic_key/content).

    `content` follows Engram's documented Memory Protocol format:
    **What** / **Why** / **Where** / **Learned**.
    """

    title: str
    type: str
    topic_key: str
    what: str
    why: str
    where: str
    learned: str = ""
    project: str | None = None
    scope: str = "project"
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def content(self) -> str:
        lines = [
            f"**What**: {self.what}",
            f"**Why**: {self.why}",
            f"**Where**: {self.where}",
        ]
        if self.learned:
            lines.append(f"**Learned**: {self.learned}")
        return "\n".join(lines)

    @property
    def content_hash(self) -> str:
        payload = f"{self.title}|{self.type}|{self.content}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "type": self.type,
            "topic_key": self.topic_key,
            "content": self.content,
            "project": self.project or "",
            "scope": self.scope,
        }


def build_mem_save_payload(
    *,
    title: str,
    type_: str,
    what: str,
    why: str,
    where: str,
    learned: str = "",
    topic_key: str,
    project: str | None = None,
    scope: str = "project",
) -> MemSavePayload:
    return MemSavePayload(
        title=title,
        type=type_,
        topic_key=topic_key,
        what=what[:_MAX_WHAT_LEN],
        why=why,
        where=where,
        learned=learned,
        project=project,
        scope=scope,
    )


def topic_key_from_graph_node(node, *, prefix: str = _DEFAULT_PREFIX) -> str:
    """Stable topic_key for a single graph node (id takes priority over path)."""
    identifier = node.id or node.path or node.label
    return topic_key_from_parts("node", identifier, prefix=prefix)
