from __future__ import annotations

from context_bridge.engram.client import EngramClient
from context_bridge.engram.config import EngramConfig
from context_bridge.engram.dedup import find_existing_by_topic_key, save_or_update
from context_bridge.engram.payloads import build_mem_save_payload
from context_bridge.engram import probe as probe_module


def _payload(topic_key="cb-layer-api"):
    return build_mem_save_payload(
        title="Architecture layer: API",
        type_="architecture",
        what="42 nodes",
        why="sync",
        where="kg.json#layer:api",
        topic_key=topic_key,
        project="demo",
    )


def test_backend_prefers_http_when_available(monkeypatch):
    monkeypatch.setattr(probe_module, "probe_http", lambda cfg: probe_module.ProbeResult("http", True, "ok"))
    monkeypatch.setattr(probe_module, "probe_cli", lambda **k: probe_module.ProbeResult("cli", True, "ok"))
    client = EngramClient(EngramConfig(base_url="http://x", http_token=None, default_project=None))
    # client module imported probe_http/probe_cli directly; patch there too
    import context_bridge.engram.client as client_module

    monkeypatch.setattr(client_module, "probe_http", lambda cfg: probe_module.ProbeResult("http", True, "ok"))
    monkeypatch.setattr(client_module, "probe_cli", lambda **k: probe_module.ProbeResult("cli", True, "ok"))
    assert client.backend == "http"


def test_backend_falls_back_to_cli(monkeypatch):
    import context_bridge.engram.client as client_module

    monkeypatch.setattr(client_module, "probe_http", lambda cfg: probe_module.ProbeResult("http", False, "down"))
    monkeypatch.setattr(client_module, "probe_cli", lambda **k: probe_module.ProbeResult("cli", True, "ok"))
    client = EngramClient(EngramConfig(base_url="http://x", http_token=None, default_project=None))
    assert client.backend == "cli"


def test_backend_unavailable_raises_on_use(monkeypatch):
    import context_bridge.engram.client as client_module

    monkeypatch.setattr(client_module, "probe_http", lambda cfg: probe_module.ProbeResult("http", False, "down"))
    monkeypatch.setattr(client_module, "probe_cli", lambda **k: probe_module.ProbeResult("cli", False, "down"))
    client = EngramClient(EngramConfig(base_url="http://x", http_token=None, default_project=None))
    assert client.backend == "unavailable"
    try:
        client.search("q")
        assert False, "expected EngramConnectionError"
    except Exception as e:  # noqa: BLE001
        assert "unreachable" in str(e)


def test_save_or_update_creates_when_missing(monkeypatch):
    class FakeClient:
        def search(self, query, project=None, limit=10):
            return []

        def save(self, payload):
            return {"id": 7, "topic_key": payload.topic_key}

    outcome = save_or_update(FakeClient(), _payload())
    assert outcome.action == "created"
    assert outcome.observation_id == 7


def test_save_or_update_updates_when_topic_key_matches(monkeypatch):
    class FakeClient:
        def search(self, query, project=None, limit=10):
            return [{"id": 3, "topic_key": "cb-layer-api"}]

        def update(self, obs_id, payload):
            return {"id": obs_id, "updated": True}

    outcome = save_or_update(FakeClient(), _payload())
    assert outcome.action == "updated"
    assert outcome.observation_id == 3


def test_find_existing_ignores_non_matching_topic_key():
    class FakeClient:
        def search(self, query, project=None, limit=10):
            return [{"id": 1, "topic_key": "cb-other"}]

    assert find_existing_by_topic_key(FakeClient(), "cb-layer-api") is None
