"""Unit tests for M1 RSS Fetcher."""

from datetime import datetime

import httpx
import pytest
from fetcher.exceptions import FetchError
from fetcher.rss_fetcher import fetch_all_sources, fetch_source
from fetcher.sources import RSSSource

SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>台積電 Q2 法說會釋出樂觀展望</title>
      <link>https://example.com/article/1</link>
      <description>台積電於 Q2 法說會上表示...</description>
      <pubDate>Thu, 16 May 2026 08:30:00 +0000</pubDate>
    </item>
    <item>
      <title>聯準會維持利率不變</title>
      <link>https://example.com/article/2</link>
      <description>聯準會宣布...</description>
      <pubDate>Thu, 16 May 2026 07:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""


class TestFetchSource:
    def test_fetch_source_success(self) -> None:
        """MockTransport 回傳合法 RSS XML，驗證 RawArticle 欄位正確。"""
        source = RSSSource("測試媒體", "https://example.com/feed", max_articles=30)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=SAMPLE_RSS_XML)

        transport = httpx.MockTransport(handler)
        with httpx.Client(transport=transport) as client:
            articles = fetch_source(source, client=client)

        assert len(articles) == 2
        assert articles[0].title == "台積電 Q2 法說會釋出樂觀展望"
        assert articles[0].url == "https://example.com/article/1"
        assert articles[0].source == "測試媒體"
        assert isinstance(articles[0].published_at, datetime)
        assert articles[0].published_at.tzinfo is not None

    def test_fetch_source_http_error(self) -> None:
        """MockTransport 回傳 500，驗證 FetchError 被拋出。"""
        source = RSSSource("測試媒體", "https://example.com/feed")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        transport = httpx.MockTransport(handler)
        with httpx.Client(transport=transport) as client:
            with pytest.raises(FetchError) as exc_info:
                fetch_source(source, client=client)

        assert "HTTP 500" in str(exc_info.value)

    def test_fetch_source_timeout(self) -> None:
        """MockTransport 拋出 TimeoutException，驗證 FetchError 被拋出。"""
        source = RSSSource("測試媒體", "https://example.com/feed")

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("timed out")

        transport = httpx.MockTransport(handler)
        with httpx.Client(transport=transport) as client:
            with pytest.raises(FetchError) as exc_info:
                fetch_source(source, client=client)

        assert "timeout" in str(exc_info.value)


class TestFetchAllSources:
    def _make_sources(self, count: int) -> list[RSSSource]:
        return [RSSSource(f"媒體{i}", f"https://example{i}.com/feed") for i in range(count)]

    def _make_handler(self, fail_indices: set[int], sources: list[RSSSource]):
        url_to_index = {s.url: i for i, s in enumerate(sources)}

        def handler(request: httpx.Request) -> httpx.Response:
            idx = url_to_index.get(str(request.url), -1)
            if idx in fail_indices:
                return httpx.Response(500)
            return httpx.Response(200, text=SAMPLE_RSS_XML)

        return handler

    def test_fetch_all_sources_one_fails(self) -> None:
        """6 個來源，其中 1 個 500，驗證回傳 5 個來源的文章。"""
        sources = self._make_sources(6)
        handler = self._make_handler({0}, sources)
        transport = httpx.MockTransport(handler)
        with httpx.Client(transport=transport) as client:
            articles = fetch_all_sources(sources=sources, client=client)

        # 5 個成功來源，每個 2 篇
        assert len(articles) == 10

    def test_fetch_all_sources_all_fail(self) -> None:
        """6 個來源全部 500，驗證回傳 []。"""
        sources = self._make_sources(6)
        handler = self._make_handler({0, 1, 2, 3, 4, 5}, sources)
        transport = httpx.MockTransport(handler)
        with httpx.Client(transport=transport) as client:
            articles = fetch_all_sources(sources=sources, client=client)

        assert articles == []
