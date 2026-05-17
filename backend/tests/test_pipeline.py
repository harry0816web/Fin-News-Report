"""Integration tests for M6 Orchestrator pipeline."""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from analyzer.exceptions import GeminiAPIError, GeminiQuotaError
from analyzer.models import AnalyzedArticle
from fetcher.models import RawArticle
from orchestrator.pipeline import run_daily_pipeline
from storage.in_memory_storage import InMemoryStorageClient
from storage.models import DailyDigest


def make_raw_article(idx: int = 0) -> RawArticle:
    return RawArticle(
        title=f"原始文章 {idx}",
        url=f"https://example.com/{idx}",
        source="測試媒體",
        published_at=datetime.now(tz=timezone.utc),
        description=f"描述 {idx}",
    )


def make_analyzed_article(idx: int = 0) -> AnalyzedArticle:
    return AnalyzedArticle(
        id=f"uuid-{idx}",
        title=f"分析文章 {idx}",
        url=f"https://example.com/{idx}",
        source="測試媒體",
        published_at="2026-05-16T08:00:00+08:00",
        category="科技股市",
        summary="摘要",
        impact_analysis="影響",
        sentiment="positive",
    )


def make_mock_analyzer(analyzed: list[AnalyzedArticle]) -> MagicMock:
    mock = MagicMock()
    mock.analyze.return_value = analyzed
    return mock


def make_mock_notifier() -> MagicMock:
    return MagicMock()


class TestPipeline:
    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_success(self, mock_fetch: MagicMock) -> None:
        """正常流程：驗證 digest 存入 storage，email 發送，回傳 status='success'。"""
        raw = [make_raw_article(i) for i in range(5)]
        analyzed = [make_analyzed_article(i) for i in range(3)]
        mock_fetch.return_value = raw

        storage = InMemoryStorageClient()
        storage.add_subscriber("user@example.com")
        notifier = make_mock_notifier()
        analyzer = make_mock_analyzer(analyzed)

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "success"
        assert result.article_count == 3
        notifier.send_daily_digest.assert_called_once()
        # 確認 digest 已存入 storage
        today = datetime.now(tz=timezone(timedelta(hours=8))).date()
        saved = storage.get_daily_digest(today)
        assert saved is not None
        assert saved.article_count == 3

    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_no_articles(self, mock_fetch: MagicMock) -> None:
        """fetch 回傳空列表，驗證回傳 status='failed'，不呼叫 analyzer。"""
        mock_fetch.return_value = []

        storage = InMemoryStorageClient()
        notifier = make_mock_notifier()
        analyzer = make_mock_analyzer([])

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "failed"
        analyzer.analyze.assert_not_called()

    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_quota_exceeded(self, mock_fetch: MagicMock) -> None:
        """analyzer 拋出 GeminiQuotaError，發送 quota 通知，回傳 status='quota_exceeded'。"""
        mock_fetch.return_value = [make_raw_article()]

        storage = InMemoryStorageClient()
        storage.add_subscriber("user@example.com")
        notifier = make_mock_notifier()
        analyzer = MagicMock()
        analyzer.analyze.side_effect = GeminiQuotaError("quota exceeded")

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "quota_exceeded"
        notifier.send_quota_exceeded_notice.assert_called_once()

    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_api_error(self, mock_fetch: MagicMock) -> None:
        """analyzer 拋出 GeminiAPIError，回傳 status='failed'，不存入 storage。"""
        mock_fetch.return_value = [make_raw_article()]

        storage = InMemoryStorageClient()
        notifier = make_mock_notifier()
        analyzer = MagicMock()
        analyzer.analyze.side_effect = GeminiAPIError("api error")

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "failed"
        assert "api error" in result.error_message
        # 確認沒有存入 storage
        today = datetime.now(tz=timezone(timedelta(hours=8))).date()
        assert storage.get_daily_digest(today) is None

    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_no_subscribers(self, mock_fetch: MagicMock) -> None:
        """正常流程但 storage 無訂閱者，驗證 send_daily_digest 未被呼叫。"""
        mock_fetch.return_value = [make_raw_article()]

        storage = InMemoryStorageClient()  # 無訂閱者
        notifier = make_mock_notifier()
        analyzer = make_mock_analyzer([make_analyzed_article()])

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "success"
        notifier.send_daily_digest.assert_not_called()

    @patch("orchestrator.pipeline.fetch_all_sources")
    def test_pipeline_cleanup_called(self, mock_fetch: MagicMock) -> None:
        """驗證 cleanup_old_digests 在 save 之後被呼叫。"""
        mock_fetch.return_value = [make_raw_article()]

        storage = InMemoryStorageClient()
        notifier = make_mock_notifier()
        analyzer = make_mock_analyzer([make_analyzed_article()])

        # 加入超過 7 天的舊資料
        old_date = date.today() - timedelta(days=10)
        storage.save_daily_digest(
            DailyDigest(
                date=str(old_date),
                generated_at=f"{old_date}T09:00:00+08:00",
                article_count=0,
                articles=[],
            )
        )

        result = run_daily_pipeline(storage, notifier, analyzer)

        assert result.status == "success"
        # 確認舊資料已被清理
        assert storage.get_daily_digest(old_date) is None
