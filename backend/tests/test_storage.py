"""Unit tests for M4 Storage — using InMemoryStorageClient."""

from datetime import date, datetime, timedelta, timezone

from analyzer.models import AnalyzedArticle
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
        impact_analysis="影響分析",
        sentiment="positive",
    )


def make_digest(date_str: str, count: int = 1) -> DailyDigest:
    articles = [make_article(i) for i in range(count)]
    return DailyDigest(
        date=date_str,
        generated_at=f"{date_str}T09:00:00+08:00",
        article_count=count,
        articles=articles,
    )


class TestDailyDigest:
    def test_save_and_get_daily_digest(self) -> None:
        storage = InMemoryStorageClient()
        digest = make_digest("2026-05-16", count=2)
        storage.save_daily_digest(digest)
        result = storage.get_daily_digest(date(2026, 5, 16))
        assert result is not None
        assert result.date == "2026-05-16"
        assert result.article_count == 2
        assert len(result.articles) == 2

    def test_get_nonexistent_digest(self) -> None:
        storage = InMemoryStorageClient()
        result = storage.get_daily_digest(date(2026, 1, 1))
        assert result is None

    def test_list_available_dates_sorted(self) -> None:
        storage = InMemoryStorageClient()
        storage.save_daily_digest(make_digest("2026-05-14"))
        storage.save_daily_digest(make_digest("2026-05-16"))
        storage.save_daily_digest(make_digest("2026-05-15"))
        dates = storage.list_available_dates()
        assert dates == sorted(dates, reverse=True)
        assert len(dates) == 3

    def test_list_available_dates_max_7(self) -> None:
        storage = InMemoryStorageClient()
        today = date(2026, 5, 16)
        for i in range(10):
            d = today - timedelta(days=i)
            storage.save_daily_digest(make_digest(str(d)))
        dates = storage.list_available_dates()
        assert len(dates) == 7

    def test_cleanup_old_digests(self) -> None:
        storage = InMemoryStorageClient()
        today = datetime.now(tz=timezone.utc).date()
        # 加入 3 筆舊資料（超過 7 天）
        for i in range(8, 11):
            d = today - timedelta(days=i)
            storage.save_daily_digest(make_digest(str(d)))
        # 加入 2 筆近期資料
        storage.save_daily_digest(make_digest(str(today)))
        storage.save_daily_digest(make_digest(str(today - timedelta(days=1))))

        deleted = storage.cleanup_old_digests(keep_days=7)
        assert deleted == 3
        remaining = storage.list_available_dates()
        assert len(remaining) == 2


class TestSubscribers:
    def test_add_subscriber_success(self) -> None:
        storage = InMemoryStorageClient()
        result = storage.add_subscriber("test@example.com")
        assert result is True
        assert len(storage.get_subscribers()) == 1

    def test_add_subscriber_duplicate(self) -> None:
        storage = InMemoryStorageClient()
        storage.add_subscriber("test@example.com")
        result = storage.add_subscriber("test@example.com")
        assert result is False
        assert len(storage.get_subscribers()) == 1

    def test_remove_subscriber_success(self) -> None:
        storage = InMemoryStorageClient()
        storage.add_subscriber("test@example.com")
        result = storage.remove_subscriber("test@example.com")
        assert result is True
        assert len(storage.get_subscribers()) == 0

    def test_remove_subscriber_not_found(self) -> None:
        storage = InMemoryStorageClient()
        result = storage.remove_subscriber("notexist@example.com")
        assert result is False


class TestDailyDigestSerialization:
    def test_to_dict_and_from_dict_roundtrip(self) -> None:
        digest = make_digest("2026-05-16", count=1)
        d = digest.to_dict()
        restored = DailyDigest.from_dict(d)
        assert restored.date == digest.date
        assert restored.article_count == digest.article_count
        assert len(restored.articles) == 1
        assert restored.articles[0].id == digest.articles[0].id
