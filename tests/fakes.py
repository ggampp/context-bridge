from __future__ import annotations


class FakeEngramClient:
    """In-memory stand-in for EngramClient, shared across sync tests."""

    def __init__(self) -> None:
        self.backend = "fake"
        self.saved: dict[int, dict] = {}
        self._next_id = 1

    def search(self, query, project=None, limit=10):
        return [
            {"id": obs_id, "topic_key": rec["topic_key"]}
            for obs_id, rec in self.saved.items()
            if rec["topic_key"] == query or query in rec["topic_key"]
        ]

    def save(self, payload):
        obs_id = self._next_id
        self._next_id += 1
        self.saved[obs_id] = {"topic_key": payload.topic_key, "content": payload.content}
        return {"id": obs_id}

    def update(self, observation_id, payload):
        self.saved[observation_id] = {"topic_key": payload.topic_key, "content": payload.content}
        return {"id": observation_id}
