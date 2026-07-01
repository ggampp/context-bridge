from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from context_bridge.engram.client import EngramClient
from context_bridge.engram.payloads import MemSavePayload


@dataclass(frozen=True)
class SaveOutcome:
    action: str  # created | updated
    observation_id: int | str | None
    response: dict[str, Any]


def find_existing_by_topic_key(
    client: EngramClient,
    topic_key: str,
    *,
    project: str | None = None,
) -> dict[str, Any] | None:
    """Search Engram for an observation with an exact topic_key match."""
    results = client.search(topic_key, project=project, limit=5)
    for item in results:
        if isinstance(item, dict) and item.get("topic_key") == topic_key:
            return item
    return None


def save_or_update(client: EngramClient, payload: MemSavePayload) -> SaveOutcome:
    """Idempotent save: update the existing observation for this topic_key,
    or create a new one if none exists yet.
    """
    existing = find_existing_by_topic_key(client, payload.topic_key, project=payload.project)
    if existing and existing.get("id") is not None:
        response = client.update(existing["id"], payload)
        return SaveOutcome("updated", existing.get("id"), response)

    response = client.save(payload)
    obs_id = response.get("id") if isinstance(response, dict) else None
    return SaveOutcome("created", obs_id, response)
