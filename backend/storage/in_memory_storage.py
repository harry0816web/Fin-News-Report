from __future__ import annotations

from datetime import date as Date
from datetime import datetime, timezone

from storage.abstract_storage import AbstractStorageClient
from storage.models import DailyDigest, Subscriber


class InMemoryStorageClient(AbstractStorageClient):
    """測試用的記憶體實作，行為與 BlobStorageClient 一致。"""

    def __init__(self) -> None:
        self._digests: dict[str, DailyDigest] = {}
        self._subscribers: list[Subscriber] = []

    def save_daily_digest(self, digest: DailyDigest) -> None:
        self._digests[digest.date] = digest

    def get_daily_digest(self, date: Date) -> DailyDigest | None:
        return self._digests.get(str(date))

    def list_available_dates(self) -> list[Date]:
        dates = sorted(
            [Date.fromisoformat(d) for d in self._digests.keys()],
            reverse=True,
        )
        return dates[:7]

    def cleanup_old_digests(self, keep_days: int = 7) -> int:
        today = datetime.now(tz=timezone.utc).date()
        to_delete = [
            d
            for d in list(self._digests.keys())
            if (today - Date.fromisoformat(d)).days > keep_days
        ]
        for d in to_delete:
            del self._digests[d]
        return len(to_delete)

    def get_subscribers(self) -> list[Subscriber]:
        return list(self._subscribers)

    def add_subscriber(self, email: str) -> bool:
        if any(s.email == email for s in self._subscribers):
            return False
        self._subscribers.append(
            Subscriber(
                email=email,
                subscribed_at=datetime.now(tz=timezone.utc).isoformat(),
            )
        )
        return True

    def remove_subscriber(self, email: str) -> bool:
        original_len = len(self._subscribers)
        self._subscribers = [s for s in self._subscribers if s.email != email]
        return len(self._subscribers) < original_len
