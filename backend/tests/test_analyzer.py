"""Unit tests for M3 AI Analyzer."""

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from analyzer.exceptions import GeminiAPIError, GeminiQuotaError, GeminiResponseParseError
from analyzer.gemini_analyzer import GeminiAnalyzer
from fetcher.models import RawArticle


def make_raw_article(title: str = "台積電財報") -> RawArticle:
    return RawArticle(
        title=title,
        url="https://example.com/article",
        source="經濟日報",
        published_at=datetime(2026, 5, 16, 8, 30, tzinfo=timezone.utc),
        description="描述內容",
    )


def make_valid_response_json(count: int = 10) -> str:
    articles = [
        {
            "title": f"文章標題 {i}",
            "url": f"https://example.com/{i}",
            "source": "經濟日報",
            "published_at": "2026-05-16T08:30:00+00:00",
            "category": "科技股市",
            "summary": f"摘要內容 {i}",
            "impact_analysis": f"影響分析 {i}",
            "sentiment": "positive",
        }
        for i in range(count)
    ]
    return json.dumps(articles)


def make_mock_client(response_text: str) -> MagicMock:
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client = MagicMock()
    mock_client.generate_content.return_value = mock_response
    return mock_client


class TestGeminiAnalyzer:
    def test_analyze_success(self) -> None:
        """mock client 回傳 10 篇合法 JSON，驗證 AnalyzedArticle 欄位正確，id 為 UUID。"""
        client = make_mock_client(make_valid_response_json(10))
        analyzer = GeminiAnalyzer(api_key="fake-key", client=client)
        articles = [make_raw_article(f"文章 {i}") for i in range(15)]

        result = analyzer.analyze(articles)

        assert len(result) == 10
        for art in result:
            assert art.title.startswith("文章標題")
            assert art.category == "科技股市"
            assert art.sentiment == "positive"
            uuid.UUID(art.id)  # 若不合法會拋出 ValueError

    def test_analyze_quota_exceeded(self) -> None:
        """mock client 拋出 429 相關錯誤，驗證拋出 GeminiQuotaError。"""
        mock_client = MagicMock()
        mock_client.generate_content.side_effect = Exception("429 Quota exceeded")
        analyzer = GeminiAnalyzer(api_key="fake-key", client=mock_client)

        with pytest.raises(GeminiQuotaError):
            analyzer.analyze([make_raw_article()])

    def test_analyze_api_error_with_retry(self) -> None:
        """mock client 連續拋出 500 錯誤，驗證重試 3 次後拋出 GeminiAPIError。"""
        mock_client = MagicMock()
        mock_client.generate_content.side_effect = Exception("500 Internal Server Error")
        analyzer = GeminiAnalyzer(api_key="fake-key", client=mock_client)

        import unittest.mock

        with unittest.mock.patch("analyzer.gemini_analyzer.time.sleep"):
            with pytest.raises(GeminiAPIError):
                analyzer.analyze([make_raw_article()])

        assert mock_client.generate_content.call_count == 3

    def test_analyze_invalid_json(self) -> None:
        """mock client 回傳非 JSON 字串，驗證拋出 GeminiResponseParseError。"""
        client = make_mock_client("這不是 JSON 格式")
        analyzer = GeminiAnalyzer(api_key="fake-key", client=client)

        with pytest.raises(GeminiResponseParseError):
            analyzer.analyze([make_raw_article()])

    def test_analyze_missing_field(self) -> None:
        """mock client 回傳缺少必要欄位的 JSON，驗證拋出 GeminiResponseParseError。"""
        incomplete = json.dumps([{"title": "只有標題，沒有其他欄位"}])
        client = make_mock_client(incomplete)
        analyzer = GeminiAnalyzer(api_key="fake-key", client=client)

        with pytest.raises(GeminiResponseParseError):
            analyzer.analyze([make_raw_article()])
