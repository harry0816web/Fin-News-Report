from abc import ABC, abstractmethod
from datetime import date as Date

from storage.models import DailyDigest, Subscriber


class AbstractStorageClient(ABC):
    @abstractmethod
    def save_daily_digest(self, digest: DailyDigest) -> None: ...

    @abstractmethod
    def get_daily_digest(self, date: Date) -> DailyDigest | None: ...

    @abstractmethod
    def list_available_dates(self) -> list[Date]: ...

    @abstractmethod
    def cleanup_old_digests(self, keep_days: int = 7) -> int: ...

    @abstractmethod
    def get_subscribers(self) -> list[Subscriber]: ...

    @abstractmethod
    def add_subscriber(self, email: str) -> bool: ...

    @abstractmethod
    def remove_subscriber(self, email: str) -> bool: ...
