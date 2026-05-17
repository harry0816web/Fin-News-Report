# M1 — RSS Fetcher

> **層級**：Backend  
> **依賴**：M0 完成  
> **相關檔案**：`backend/fetcher/`

---

## 任務列表

### T1-1 建立 `RawArticle` dataclass

**檔案**：`backend/fetcher/models.py`

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RawArticle:
    title: str
    url: str
    source: str
    published_at: datetime
    description: str
```

**驗收**：`from fetcher.models import RawArticle` 可正常 import

---

### T1-2 建立 `RSSSource` dataclass 與來源設定

**檔案**：`backend/fetcher/sources.py`

```python
from dataclasses import dataclass, field

@dataclass
class RSSSource:
    name: str
    url: str
    max_articles: int = 30

RSS_SOURCES: list[RSSSource] = [
    RSSSource("經濟日報",  "https://money.udn.com/rssfeed/news/1/1001?ch=money"),
    RSSSource("工商時報",  "https://ctee.com.tw/feed"),
    RSSSource("鉅亨網",    "https://feeds.cnyes.com/market/tw/news.xml"),
    RSSSource("MoneyDJ",  "https://www.moneydj.com/rss/news.aspx"),
    RSSSource("Yahoo財經", "https://tw.news.yahoo.com/rss/finance"),
    RSSSource("科技新報",  "https://technews.tw/feed/"),
]
```

**驗收**：`from fetcher.sources import RSS_SOURCES` 且 `len(RSS_SOURCES) == 6`

---

### T1-3 建立自定義例外

**檔案**：`backend/fetcher/exceptions.py`

```python
class FetchError(Exception):
    """單一 RSS 來源抓取失敗"""
    def __init__(self, source_name: str, reason: str):
        self.source_name = source_name
        super().__init__(f"Failed to fetch {source_name}: {reason}")
```

**驗收**：可 raise 與 catch `FetchError`

---

### T1-4 實作 `fetch_source()`

**檔案**：`backend/fetcher/rss_fetcher.py`

- 使用 `httpx.get()` 下載 RSS，timeout=10 秒
- 使用 `feedparser.parse()` 解析
- 取前 `source.max_articles` 則
- 解析 `entry.published_parsed` 或 `entry.updated_parsed` 轉為 `datetime`（帶 UTC 時區）
- HTTP 非 200 或 feedparser 失敗時拋出 `FetchError`

```python
import httpx
import feedparser
from datetime import datetime, timezone

def fetch_source(
    source: RSSSource,
    client: httpx.Client | None = None,
) -> list[RawArticle]:
    ...
```

**驗收**：傳入合法 RSSSource 且使用 `httpx.MockTransport` 模擬時，回傳正確 `list[RawArticle]`

---

### T1-5 實作 `fetch_all_sources()`

**檔案**：`backend/fetcher/rss_fetcher.py`（同上）

- 迭代 `RSS_SOURCES`，呼叫 `fetch_source()`
- 捕捉 `FetchError`，記錄 `logging.warning()`，繼續下一來源
- 若所有來源皆失敗，記錄 `logging.error()` 並回傳空列表

```python
def fetch_all_sources(
    sources: list[RSSSource] | None = None,
    client: httpx.Client | None = None,
) -> list[RawArticle]:
    ...
```

**驗收**：
- 正常情況：回傳多來源合併的文章列表
- 單一來源失敗：僅該來源被跳過，其餘文章正常回傳
- 所有來源失敗：回傳 `[]`

---

### T1-6 撰寫單元測試

**檔案**：`backend/tests/test_fetcher.py`

| 測試案例 | 情境 |
|---------|------|
| `test_fetch_source_success` | MockTransport 回傳合法 RSS XML，驗證 RawArticle 欄位正確 |
| `test_fetch_source_http_error` | MockTransport 回傳 500，驗證 FetchError 被拋出 |
| `test_fetch_source_timeout` | MockTransport 拋出 httpx.TimeoutException，驗證 FetchError 被拋出 |
| `test_fetch_all_sources_one_fails` | 6 個來源，其中 1 個 500，驗證回傳 5 個來源的文章 |
| `test_fetch_all_sources_all_fail` | 6 個來源全部 500，驗證回傳 `[]` |

**執行**：`uv run pytest backend/tests/test_fetcher.py -v`

**驗收**：所有測試通過，無 warning

---

## 完成條件

- [ ] T1-1 RawArticle dataclass 建立
- [ ] T1-2 RSSSource 與 RSS_SOURCES 建立
- [ ] T1-3 FetchError 例外建立
- [ ] T1-4 fetch_source() 實作完成
- [ ] T1-5 fetch_all_sources() 實作完成
- [ ] T1-6 所有單元測試通過
