from __future__ import annotations


class EngramError(Exception):
    """Base error for all Engram client failures."""


class EngramConnectionError(EngramError):
    """Raised when neither HTTP nor CLI backend is reachable."""


class EngramNotFoundError(EngramError):
    """Raised when a requested resource (observation, etc.) does not exist."""
