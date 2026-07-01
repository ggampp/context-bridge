from __future__ import annotations

from typing import Any

from context_bridge.enrich.pipeline import EnrichResult


def format_json_dict(result: EnrichResult) -> dict[str, Any]:
    """Stable, versioned JSON schema for `context-bridge enrich --json`."""
    return result.to_dict()
