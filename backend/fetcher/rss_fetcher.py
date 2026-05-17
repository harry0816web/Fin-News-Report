import logging
from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx
from fetcher.exceptions import FetchError
from fetcher.models import RawArticle
from fetcher.sources import RSS_SOURCES, RSSSource


def _parse_time(time_struct: struct_time | None) -> datetime:
    """將 feedparser 的 time_struct 轉換為帶 UTC 時區的 datetime。"""
    if time_struct is None:
        return datetime.now(tz=timezone.utc)
    import calendar

    timestamp = calendar.timegm(time_struct)
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def fetch_source(
    source: RSSSource,
    client: httpx.Client | None = None,
) -> list[RawArticle]:
    """
    抓取單一 RSS 來源。
    失敗時拋出 FetchError。
    """
    own_client = client is None
    _client: httpx.Client = client if client is not None else httpx.Client(timeout=10.0)
    try:
        try:
            response = _client.get(source.url)
        except httpx.TimeoutException as e:
            raise FetchError(source.name, f"timeout: {e}") from e
        except httpx.RequestError as e:
            raise FetchError(source.name, f"request error: {e}") from e

        if response.status_code != 200:
            raise FetchError(source.name, f"HTTP {response.status_code}")

        feed = feedparser.parse(response.text)
        if feed.bozo and not feed.entries:
            raise FetchError(source.name, "feedparser parse error")

        articles: list[RawArticle] = []
        for entry in feed.entries[: source.max_articles]:
            time_struct = getattr(entry, "published_parsed", None) or getattr(
                entry, "updated_parsed", None
            )
            published_at = _parse_time(time_struct)
            articles.append(
                RawArticle(
                    title=entry.get("title", "").strip(),
                    url=entry.get("link", ""),
                    source=source.name,
                    published_at=published_at,
                    description=entry.get("summary", "").strip(),
                )
            )
        return articles
    finally:
        if own_client:
            _client.close()


def fetch_all_sources(
    sources: list[RSSSource] | None = None,
    client: httpx.Client | None = None,
) -> list[RawArticle]:
    """
    抓取所有設定來源的 RSS Feed。
    單一來源失敗時記錄 warning 並跳過，不拋出例外。
    回傳：所有成功來源的文章合併列表（不去重）。
    """
    if sources is None:
        sources = RSS_SOURCES

    all_articles: list[RawArticle] = []
    failed_count = 0

    for source in sources:
        try:
            articles = fetch_source(source, client=client)
            all_articles.extend(articles)
        except FetchError as e:
            logging.warning("Skipping source due to error: %s", e)
            failed_count += 1

    if failed_count == len(sources):
        logging.error("All RSS sources failed. No articles fetched.")

    return all_articles
