from __future__ import annotations

from typing import Any

from context_bridge.engram.cli_client import EngramCliClient
from context_bridge.engram.config import EngramConfig, load_engram_config
from context_bridge.engram.errors import EngramConnectionError, EngramError
from context_bridge.engram.http_client import EngramHttpClient
from context_bridge.engram.payloads import MemSavePayload
from context_bridge.engram.probe import probe_cli, probe_http


class EngramClient:
    """Facade that prefers the Engram HTTP API and falls back to the CLI.

    Backend selection happens once (lazily, on first use) and is cached for
    the lifetime of the client instance. Construction never raises — failures
    surface only when an operation actually needs a backend.
    """

    def __init__(self, config: EngramConfig | None = None) -> None:
        self.config = config or load_engram_config()
        self._backend: str | None = None
        self._http = EngramHttpClient(self.config)
        self._cli = EngramCliClient()
        self._session_id: str | None = None

    @property
    def backend(self) -> str:
        if self._backend is None:
            self._backend = self._select_backend()
        return self._backend

    def _select_backend(self) -> str:
        if probe_http(self.config).available:
            return "http"
        if probe_cli().available:
            return "cli"
        return "unavailable"

    def _require_backend(self) -> str:
        backend = self.backend
        if backend == "unavailable":
            raise EngramConnectionError(
                "Engram is unreachable: start `engram serve` or ensure `engram` is in PATH."
            )
        return backend

    def stats(self) -> dict[str, Any]:
        backend = self._require_backend()
        return self._http.stats() if backend == "http" else self._cli.stats()

    def context(self, *, project: str | None = None) -> dict[str, Any]:
        backend = self._require_backend()
        if backend == "http":
            return self._http.context(project=project)
        raise EngramError("`context` is only available via the Engram HTTP backend")

    def search(
        self,
        query: str,
        *,
        project: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        backend = self._require_backend()
        if backend == "http":
            return self._http.search(query, project=project, limit=limit)
        return self._cli.search(query, project=project, limit=limit)

    def save(self, payload: MemSavePayload) -> dict[str, Any]:
        backend = self._require_backend()
        project = payload.project or self.config.default_project
        if backend == "http":
            if self._session_id is None:
                self._session_id = self._http.ensure_session(project=project)
            return self._http.save_observation(
                session_id=self._session_id,
                type_=payload.type,
                title=payload.title,
                content=payload.content,
                project=project,
                scope=payload.scope,
                topic_key=payload.topic_key,
            )
        return self._cli.save(
            title=payload.title,
            content=payload.content,
            type_=payload.type,
            project=project,
            topic_key=payload.topic_key,
        )

    def update(self, observation_id: int | str, payload: MemSavePayload) -> dict[str, Any]:
        backend = self._require_backend()
        if backend == "http":
            return self._http.update_observation(
                observation_id,
                title=payload.title,
                content=payload.content,
                type=payload.type,
                topic_key=payload.topic_key,
            )
        # CLI fallback has no update verb; recreate with the same topic_key
        # so the server-side upsert-by-topic_key path applies.
        return self.save(payload)
