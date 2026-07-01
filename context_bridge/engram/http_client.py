from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from uuid import uuid4

from context_bridge.engram.config import EngramConfig
from context_bridge.engram.errors import EngramConnectionError, EngramError, EngramNotFoundError

# Endpoints below follow the public HTTP API documented in Engram's DOCS.md
# (section "HTTP API Endpoints"): /health, /search, /context, /stats,
# /sessions, /observations. context-bridge only relies on documented,
# stable routes — dashboard/cloud-only routes are out of scope.


def _build_url(base_url: str, path: str, params: dict[str, Any] | None = None) -> str:
    url = f"{base_url}{path}"
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    if clean:
        url += "?" + urllib.parse.urlencode(clean)
    return url


def _request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read().decode("utf-8") if e.fp else ""
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise EngramConnectionError(f"Cannot reach Engram HTTP API at {url}: {e}") from e

    parsed: dict[str, Any] = {}
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
    return status, parsed


class EngramHttpClient:
    """Thin REST client for `engram serve`.

    Implements the subset of the HTTP API needed by context-bridge:
    health, stats, search, context, sessions, observations (create/update).
    """

    def __init__(self, config: EngramConfig) -> None:
        self.config = config

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = _build_url(self.config.base_url, path, params)
        status, data = _request("GET", url, headers=self.config.auth_headers(), timeout=self.config.timeout)
        if status >= 400:
            raise EngramError(f"GET {path} failed ({status}): {data}")
        return data

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = _build_url(self.config.base_url, path)
        status, data = _request(
            "POST", url, headers=self.config.auth_headers(), body=body, timeout=self.config.timeout
        )
        if status >= 400:
            raise EngramError(f"POST {path} failed ({status}): {data}")
        return data

    def _patch(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = _build_url(self.config.base_url, path)
        status, data = _request(
            "PATCH", url, headers=self.config.auth_headers(), body=body, timeout=self.config.timeout
        )
        if status == 404:
            raise EngramNotFoundError(f"PATCH {path}: not found")
        if status >= 400:
            raise EngramError(f"PATCH {path} failed ({status}): {data}")
        return data

    def health(self) -> dict[str, Any]:
        return self._get("/health")

    def stats(self) -> dict[str, Any]:
        return self._get("/stats")

    def context(self, *, project: str | None = None, scope: str | None = None) -> dict[str, Any]:
        return self._get("/context", {"project": project, "scope": scope})

    def search(
        self,
        query: str,
        *,
        project: str | None = None,
        type_: str | None = None,
        scope: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        data = self._get(
            "/search",
            {"q": query, "project": project, "type": type_, "scope": scope, "limit": limit},
        )
        results = data.get("results") if isinstance(data, dict) else None
        if results is None and isinstance(data, list):
            results = data
        return results or []

    def ensure_session(self, *, project: str | None, directory: str | None = None) -> str:
        session_id = f"context-bridge-{uuid4().hex[:12]}"
        body: dict[str, Any] = {"id": session_id}
        if project:
            body["project"] = project
        if directory:
            body["directory"] = directory
        self._post("/sessions", body)
        return session_id

    def save_observation(
        self,
        *,
        session_id: str,
        type_: str,
        title: str,
        content: str,
        project: str | None = None,
        scope: str | None = None,
        topic_key: str | None = None,
        tool_name: str = "context-bridge",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "session_id": session_id,
            "type": type_,
            "title": title,
            "content": content,
            "tool_name": tool_name,
        }
        if project:
            body["project"] = project
        if scope:
            body["scope"] = scope
        if topic_key:
            body["topic_key"] = topic_key
        return self._post("/observations", body)

    def update_observation(self, observation_id: int | str, **fields: Any) -> dict[str, Any]:
        clean = {k: v for k, v in fields.items() if v is not None}
        return self._patch(f"/observations/{observation_id}", clean)
