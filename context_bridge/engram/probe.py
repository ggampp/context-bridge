from __future__ import annotations

from dataclasses import dataclass

from context_bridge.engram.cli_client import EngramCliClient
from context_bridge.engram.config import EngramConfig
from context_bridge.engram.errors import EngramError
from context_bridge.engram.http_client import EngramHttpClient


@dataclass(frozen=True)
class ProbeResult:
    backend: str  # http | cli
    available: bool
    detail: str


def probe_http(config: EngramConfig) -> ProbeResult:
    try:
        data = EngramHttpClient(config).health()
    except EngramError as e:
        return ProbeResult("http", False, str(e))
    service = data.get("service", "engram")
    version = data.get("version", "")
    return ProbeResult("http", True, f"{config.base_url} ({service} {version})".strip())


def probe_cli(*, binary: str = "engram") -> ProbeResult:
    client = EngramCliClient(binary=binary)
    if not client.is_available():
        return ProbeResult("cli", False, f"`{binary}` not found in PATH")
    try:
        version = client.version()
    except EngramError as e:
        return ProbeResult("cli", False, str(e))
    return ProbeResult("cli", True, version or "engram CLI available")
