from __future__ import annotations

import json

import pytest

from context_bridge.engram import http_client as http_client_module
from context_bridge.engram.config import EngramConfig
from context_bridge.engram.errors import EngramConnectionError, EngramError, EngramNotFoundError
from context_bridge.engram.http_client import EngramHttpClient


@pytest.fixture
def config() -> EngramConfig:
    return EngramConfig(base_url="http://127.0.0.1:7437", http_token=None, default_project="demo")


class _FakeResponse:
    def __init__(self, status: int, payload: dict) -> None:
        self.status = status
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _patch_urlopen(monkeypatch, responder):
    def fake_urlopen(req, timeout=5.0):
        return responder(req)

    monkeypatch.setattr(http_client_module.urllib.request, "urlopen", fake_urlopen)


def test_health_ok(monkeypatch, config):
    _patch_urlopen(
        monkeypatch,
        lambda req: _FakeResponse(200, {"status": "ok", "service": "engram", "version": "0.1.0"}),
    )
    client = EngramHttpClient(config)
    data = client.health()
    assert data["service"] == "engram"


def test_search_returns_results_list(monkeypatch, config):
    _patch_urlopen(
        monkeypatch,
        lambda req: _FakeResponse(200, {"results": [{"id": 1, "topic_key": "cb-layer-api"}]}),
    )
    client = EngramHttpClient(config)
    results = client.search("api", project="demo")
    assert results == [{"id": 1, "topic_key": "cb-layer-api"}]


def test_search_includes_query_params(monkeypatch, config):
    captured = {}

    def responder(req):
        captured["url"] = req.full_url
        return _FakeResponse(200, {"results": []})

    _patch_urlopen(monkeypatch, responder)
    client = EngramHttpClient(config)
    client.search("auth flow", project="demo", limit=3)
    assert "q=auth" in captured["url"]
    assert "project=demo" in captured["url"]
    assert "limit=3" in captured["url"]


def test_save_observation_posts_session_and_topic_key(monkeypatch, config):
    bodies = []

    def responder(req):
        bodies.append(json.loads(req.data.decode("utf-8")))
        return _FakeResponse(200, {"id": 42, "topic_key": "cb-x"})

    _patch_urlopen(monkeypatch, responder)
    client = EngramHttpClient(config)
    result = client.save_observation(
        session_id="sess-1",
        type_="architecture",
        title="t",
        content="c",
        project="demo",
        topic_key="cb-x",
    )
    assert result["id"] == 42
    assert bodies[0]["session_id"] == "sess-1"
    assert bodies[0]["topic_key"] == "cb-x"


def test_update_observation_404_raises_not_found(monkeypatch, config):
    class FakeHTTPError(Exception):
        code = 404
        fp = None

        def read(self):
            return b'{"error": "not found"}'

    def responder(req):
        raise http_client_module.urllib.error.HTTPError(
            req.full_url, 404, "Not Found", None, None
        )

    _patch_urlopen(monkeypatch, responder)
    client = EngramHttpClient(config)
    with pytest.raises(EngramNotFoundError):
        client.update_observation(999, title="new title")


def test_unreachable_host_raises_connection_error(monkeypatch, config):
    def responder(req):
        raise http_client_module.urllib.error.URLError("refused")

    _patch_urlopen(monkeypatch, responder)
    client = EngramHttpClient(config)
    with pytest.raises(EngramConnectionError):
        client.health()


def test_auth_header_sent_when_token_set(monkeypatch):
    config = EngramConfig(base_url="http://127.0.0.1:7437", http_token="secret", default_project=None)
    captured = {}

    def responder(req):
        captured["auth"] = req.get_header("Authorization")
        return _FakeResponse(200, {"status": "ok"})

    _patch_urlopen(monkeypatch, responder)
    EngramHttpClient(config).health()
    assert captured["auth"] == "Bearer secret"
