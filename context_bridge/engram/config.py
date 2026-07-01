from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EngramConfig:
    """Connection settings for the Engram backend.

    Mirrors the environment variables documented in Engram's README/DOCS.md:
    ENGRAM_URL, ENGRAM_PORT, ENGRAM_DATA_DIR, ENGRAM_HTTP_TOKEN, ENGRAM_PROJECT.
    """

    base_url: str
    http_token: str | None
    default_project: str | None
    timeout: float = 5.0

    def auth_headers(self) -> dict[str, str]:
        if self.http_token:
            return {"Authorization": f"Bearer {self.http_token}"}
        return {}


def load_engram_config(*, timeout: float = 5.0) -> EngramConfig:
    explicit_url = os.environ.get("ENGRAM_URL")
    if explicit_url:
        base_url = explicit_url.rstrip("/")
    else:
        port = os.environ.get("ENGRAM_PORT", "7437")
        base_url = f"http://127.0.0.1:{port}"

    return EngramConfig(
        base_url=base_url,
        http_token=os.environ.get("ENGRAM_HTTP_TOKEN") or None,
        default_project=os.environ.get("ENGRAM_PROJECT") or None,
        timeout=timeout,
    )
