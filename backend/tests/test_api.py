"""Unit tests for M7 HTTP API."""

from datetime import datetime, timedelta, timezone

from analyzer.models import AnalyzedArticle
from api.news_handler import handle_get_news, handle_get_news_dates
from api.subscribe_handler import handle_subscribe, handle_unsubscribe
from storage.in_memory_storage import InMemoryStorageClient
from storage.models import DailyDigest


def make_article(idx: int = 0) -> AnalyzedArticle:
    return AnalyzedArticle(
        id=f"uuid-{idx}",
        title=f"測試文章 {idx}",
        url=f"https://example.com/{idx}",
        source="測試媒體",
        published_at="2026-05-16T08:00:00+08:00",
        category="科技股市",
        summary="摘要",
        impact_analysis="影響",
        sentiment="positive",
    )


def make_digest(date_str: str) -> DailyDigest:
    return DailyDigest(
        date=date_str,
        generated_at=f"{date_str}T09:00:00+08:00",
        article_count=1,
        articles=[make_article()],
    )


_TW_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(tz=_TW_TZ).date()
TODAY_STR = str(TODAY)
YESTERDAY_STR = str(TODAY - timedelta(days=1))
OLD_DATE_STR = str(TODAY - timedelta(days=8))


class TestGetNews:
    def test_get_news_today_success(self) -> None:
        storage = InMemoryStorageClient()
        storage.save_daily_digest(make_digest(TODAY_STR))
        status, body = handle_get_news(None, storage)
        assert status == 200
        assert body["date"] == TODAY_STR

    def test_get_news_specific_date(self) -> None:
        storage = InMemoryStorageClient()
        storage.save_daily_digest(make_digest(YESTERDAY_STR))
        status, body = handle_get_news(YESTERDAY_STR, storage)
        assert status == 200
        assert body["date"] == YESTERDAY_STR

    def test_get_news_invalid_format(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_get_news("2026/05/16", storage)
        assert status == 400
        assert "invalid date format" in body["error"]

    def test_get_news_out_of_range(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_get_news(OLD_DATE_STR, storage)
        assert status == 400
        assert "date out of range" in body["error"]

    def test_get_news_not_found(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_get_news(YESTERDAY_STR, storage)
        assert status == 404
        assert "not found" in body["error"]


class TestGetNewsDates:
    def test_get_news_dates(self) -> None:
        storage = InMemoryStorageClient()
        storage.save_daily_digest(make_digest(TODAY_STR))
        storage.save_daily_digest(make_digest(YESTERDAY_STR))
        storage.save_daily_digest(make_digest(str(TODAY - timedelta(days=2))))
        status, body = handle_get_news_dates(storage)
        assert status == 200
        assert len(body["dates"]) == 3


class TestSubscribe:
    def test_subscribe_success(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_subscribe({"email": "test@example.com"}, storage)
        assert status == 201
        assert body["message"] == "subscribed"

    def test_subscribe_duplicate(self) -> None:
        storage = InMemoryStorageClient()
        storage.add_subscriber("test@example.com")
        status, body = handle_subscribe({"email": "test@example.com"}, storage)
        assert status == 200
        assert body["message"] == "already subscribed"

    def test_subscribe_invalid_email(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_subscribe({"email": "notanemail"}, storage)
        assert status == 400
        assert "invalid email" in body["error"]

    def test_subscribe_missing_email(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_subscribe({}, storage)
        assert status == 400
        assert "missing email" in body["error"]


class TestUnsubscribe:
    def test_unsubscribe_success(self) -> None:
        storage = InMemoryStorageClient()
        storage.add_subscriber("test@example.com")
        status, body = handle_unsubscribe("test@example.com", storage)
        assert status == 200
        assert body["message"] == "unsubscribed"

    def test_unsubscribe_not_found(self) -> None:
        storage = InMemoryStorageClient()
        status, body = handle_unsubscribe("notexist@example.com", storage)
        assert status == 200
        assert body["message"] == "not found"
