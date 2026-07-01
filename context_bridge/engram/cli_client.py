from __future__ import annotations

import json
from typing import Any

from context_bridge.core.subprocess_runner import run_command, which
from context_bridge.engram.errors import EngramConnectionError, EngramError

# Best-effort CLI fallback, used when `engram serve` (HTTP) is unreachable.
# Based on the `engram` CLI reference table in the project README. The CLI
# does not expose topic_key/PATCH-style updates as richly as the HTTP API,
# so this fallback supports create + search only; callers should prefer
# EngramHttpClient when available (see EngramClient facade).


class EngramCliClient:
    def __init__(self, *, binary: str = "engram", timeout: int = 15) -> None:
        self.binary = binary
        self.timeout = timeout

    def is_available(self) -> bool:
        return which(self.binary) is not None

    def version(self) -> str:
        result = run_command([self.binary, "version"], timeout=self.timeout)
        if not result.success:
            raise EngramConnectionError(f"`{self.binary} version` failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def stats(self) -> dict[str, Any]:
        result = run_command([self.binary, "stats", "--json"], timeout=self.timeout)
        if not result.success:
            result = run_command([self.binary, "stats"], timeout=self.timeout)
            if not result.success:
                raise EngramError(f"`{self.binary} stats` failed: {result.stderr.strip()}")
            return {"raw": result.stdout.strip()}
        return _parse_json_or_raw(result.stdout)

    def search(
        self,
        query: str,
        *,
        project: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        cmd = [self.binary, "search", query, "--limit", str(limit)]
        if project:
            cmd += ["--project", project]
        result = run_command(cmd + ["--json"], timeout=self.timeout)
        if not result.success:
            result = run_command(cmd, timeout=self.timeout)
            if not result.success:
                raise EngramError(f"`{self.binary} search` failed: {result.stderr.strip()}")
            return [{"raw": line} for line in result.stdout.strip().splitlines() if line]
        parsed = _parse_json_or_raw(result.stdout)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
            return parsed["results"]
        return []

    def save(
        self,
        *,
        title: str,
        content: str,
        type_: str | None = None,
        project: str | None = None,
        topic_key: str | None = None,
    ) -> dict[str, Any]:
        cmd = [self.binary, "save", title, content]
        if type_:
            cmd += ["--type", type_]
        if project:
            cmd += ["--project", project]
        if topic_key:
            cmd += ["--topic-key", topic_key]
        result = run_command(cmd, timeout=self.timeout)
        if not result.success:
            raise EngramError(f"`{self.binary} save` failed: {result.stderr.strip()}")
        return {"raw": result.stdout.strip()}


def _parse_json_or_raw(text: str) -> Any:
    text = text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
