"""Optional integration tests against a live Engram instance.

Skipped by default. Run explicitly with:

    pytest tests/test_integration_network.py -m network

Requires `engram serve` running locally (default http://127.0.0.1:7437) or
the `engram` CLI in PATH.
"""

from __future__ import annotations

import pytest

from context_bridge.engram.client import EngramClient
from context_bridge.engram.probe import probe_cli, probe_http
from context_bridge.engram.config import load_engram_config

pytestmark = pytest.mark.network


def _engram_available() -> bool:
    config = load_engram_config(timeout=1.0)
    return probe_http(config).available or probe_cli().available


@pytest.fixture(autouse=True)
def _skip_if_unavailable():
    if not _engram_available():
        pytest.skip("no live Engram backend reachable (HTTP or CLI)")


def test_live_engram_backend_selection():
    client = EngramClient()
    assert client.backend in {"http", "cli"}


def test_live_engram_stats_returns_dict():
    client = EngramClient()
    stats = client.stats()
    assert isinstance(stats, dict)


def test_live_engram_search_smoke():
    client = EngramClient()
    results = client.search("context-bridge", limit=5)
    assert isinstance(results, list)
