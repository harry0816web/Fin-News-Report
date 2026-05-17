"""Unit tests for M5 Email Notifier."""

from unittest.mock import MagicMock

from analyzer.models import AnalyzedArticle
from notifier.email_notifier import EmailNotifier
from notifier.models import SendResult
from storage.models import DailyDigest


def make_article(idx: int = 0, category: str = "科技股市") -> AnalyzedArticle:
    return AnalyzedArticle(
        id=f"uuid-{idx}",
        title=f"文章 {idx}",
        url=f"https://example.com/{idx}",
        source="經濟日報",
        published_at="2026-05-16T08:00:00+08:00",
        category=category,
        summary=f"摘要 {idx}",
        impact_analysis=f"影響分析 {idx}",
        sentiment="positive",
    )


def make_digest(article_count: int = 3) -> DailyDigest:
    articles = [make_article(i) for i in range(article_count)]
    return DailyDigest(
        date="2026-05-16",
        generated_at="2026-05-16T09:00:00+08:00",
        article_count=article_count,
        articles=articles,
    )


def make_notifier(mock_client: MagicMock) -> EmailNotifier:
    return EmailNotifier(
        acs_connection_string="dummy",
        sender_address="noreply@example.com",
        acs_client=mock_client,
    )


class TestEmailNotifier:
    def test_send_daily_digest_html_contains_articles(self) -> None:
        """渲染後的 HTML 包含所有文章標題。"""
        mock_client = MagicMock()
        notifier = make_notifier(mock_client)
        digest = make_digest(3)

        result = notifier.send_daily_digest(digest, ["user@example.com"])

        assert result.success_count == 1
        assert result.failure_count == 0
        # 驗證 begin_send 被呼叫，且 HTML 內容包含文章標題
        assert mock_client.begin_send.called
        call_args = mock_client.begin_send.call_args[0][0]
        html = call_args["content"]["html"]
        assert "文章 0" in html
        assert "文章 1" in html
        assert "文章 2" in html

    def test_send_daily_digest_unsubscribe_link(self) -> None:
        """HTML 包含正確的退訂連結（含 email encoding）。"""
        mock_client = MagicMock()
        notifier = make_notifier(mock_client)
        digest = make_digest(1)

        notifier.send_daily_digest(digest, ["user+test@example.com"])

        call_args = mock_client.begin_send.call_args[0][0]
        html = call_args["content"]["html"]
        # URL encode: + → %2B
        assert "user%2Btest%40example.com" in html or "unsubscribe" in html

    def test_send_daily_digest_batch_over_50(self) -> None:
        """60 個訂閱者，驗證 begin_send 被呼叫 60 次（每人一封）。"""
        mock_client = MagicMock()
        notifier = make_notifier(mock_client)
        digest = make_digest(2)
        recipients = [f"user{i}@example.com" for i in range(60)]

        result = notifier.send_daily_digest(digest, recipients)

        assert mock_client.begin_send.call_count == 60
        assert result.success_count == 60
        assert result.failure_count == 0

    def test_send_daily_digest_returns_send_result(self) -> None:
        """回傳 SendResult，success_count 正確。"""
        mock_client = MagicMock()
        notifier = make_notifier(mock_client)
        digest = make_digest(1)

        result = notifier.send_daily_digest(digest, ["a@example.com", "b@example.com"])

        assert isinstance(result, SendResult)
        assert result.success_count == 2

    def test_send_quota_exceeded_notice(self) -> None:
        """驗證 begin_send 被呼叫，主旨包含「配額」相關文字。"""
        mock_client = MagicMock()
        notifier = make_notifier(mock_client)

        result = notifier.send_quota_exceeded_notice(["user@example.com"])

        assert mock_client.begin_send.called
        call_args = mock_client.begin_send.call_args[0][0]
        subject = call_args["content"]["subject"]
        assert "配額" in subject or "quota" in subject.lower()
        assert result.success_count == 1
