from __future__ import annotations

import json
import logging
from datetime import date as Date
from datetime import datetime, timezone

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from storage.abstract_storage import AbstractStorageClient
from storage.models import DailyDigest, Subscriber

_MAX_RETRIES = 3


class BlobStorageClient(AbstractStorageClient):
    def __init__(self, connection_string: str, container_name: str = "fin-news") -> None:
        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = container_name

    def _blob_client(self, blob_name: str):  # type: ignore[no-untyped-def]
        return self._service.get_blob_client(container=self._container, blob=blob_name)

    def _container_client(self):  # type: ignore[no-untyped-def]
        return self._service.get_container_client(self._container)

    # --- 每日新聞 ---

    def save_daily_digest(self, digest: DailyDigest) -> None:
        blob = self._blob_client(f"news/{digest.date}.json")
        data = json.dumps(digest.to_dict(), ensure_ascii=False)
        blob.upload_blob(data, overwrite=True, encoding="utf-8")

    def get_daily_digest(self, date: Date) -> DailyDigest | None:
        blob = self._blob_client(f"news/{date}.json")
        try:
            content = blob.download_blob().readall().decode("utf-8")
            return DailyDigest.from_dict(json.loads(content))
        except ResourceNotFoundError:
            return None

    def list_available_dates(self) -> list[Date]:
        container = self._container_client()
        dates: list[Date] = []
        for item in container.list_blobs(name_starts_with="news/"):
            name = item["name"]  # news/YYYY-MM-DD.json
            date_str = name.removeprefix("news/").removesuffix(".json")
            try:
                dates.append(Date.fromisoformat(date_str))
            except ValueError:
                continue
        return sorted(dates, reverse=True)[:7]

    def cleanup_old_digests(self, keep_days: int = 7) -> int:
        today = datetime.now(tz=timezone.utc).date()
        container = self._container_client()
        deleted = 0
        for item in container.list_blobs(name_starts_with="news/"):
            name = item["name"]
            date_str = name.removeprefix("news/").removesuffix(".json")
            try:
                d = Date.fromisoformat(date_str)
            except ValueError:
                continue
            if (today - d).days > keep_days:
                self._blob_client(name).delete_blob()
                deleted += 1
        return deleted

    # --- 訂閱者名單 ---

    def get_subscribers(self) -> list[Subscriber]:
        blob = self._blob_client("subscribers/list.json")
        try:
            content = blob.download_blob().readall().decode("utf-8")
            data = json.loads(content)
            return [Subscriber(email=s["email"], subscribed_at=s["subscribed_at"]) for s in data]
        except ResourceNotFoundError:
            return []

    def add_subscriber(self, email: str) -> bool:
        for attempt in range(_MAX_RETRIES):
            try:
                blob = self._blob_client("subscribers/list.json")
                try:
                    download = blob.download_blob()
                    etag = download.properties["etag"]
                    subscribers = json.loads(download.readall().decode("utf-8"))
                except ResourceNotFoundError:
                    etag = None
                    subscribers = []

                if any(s["email"] == email for s in subscribers):
                    return False

                subscribers.append(
                    {
                        "email": email,
                        "subscribed_at": datetime.now(tz=timezone.utc).isoformat(),
                    }
                )
                data = json.dumps(subscribers, ensure_ascii=False)

                if etag:
                    blob.upload_blob(
                        data,
                        overwrite=True,
                        encoding="utf-8",
                        etag=etag,
                        match_condition=MatchConditions.IfNotModified,
                    )
                else:
                    blob.upload_blob(data, encoding="utf-8")
                return True
            except Exception as e:
                logging.warning("add_subscriber attempt %d failed: %s", attempt + 1, e)
                if attempt == _MAX_RETRIES - 1:
                    raise
        return False  # unreachable

    def remove_subscriber(self, email: str) -> bool:
        for attempt in range(_MAX_RETRIES):
            try:
                blob = self._blob_client("subscribers/list.json")
                try:
                    download = blob.download_blob()
                    etag = download.properties["etag"]
                    subscribers = json.loads(download.readall().decode("utf-8"))
                except ResourceNotFoundError:
                    return False

                original_len = len(subscribers)
                subscribers = [s for s in subscribers if s["email"] != email]
                if len(subscribers) == original_len:
                    return False

                data = json.dumps(subscribers, ensure_ascii=False)
                blob.upload_blob(
                    data,
                    overwrite=True,
                    encoding="utf-8",
                    etag=etag,
                    match_condition=MatchConditions.IfNotModified,
                )
                return True
            except Exception as e:
                logging.warning("remove_subscriber attempt %d failed: %s", attempt + 1, e)
                if attempt == _MAX_RETRIES - 1:
                    raise
        return False  # unreachable
