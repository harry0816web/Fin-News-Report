# 台灣財經新聞每日彙整 App — 詳細設計文件

> 版本：v1.0  
> 日期：2026-05-16  
> 狀態：草稿  
> 依據：`doc/proposal.md` v1.0

---

## 目錄

1. [文件概覽](#1-文件概覽)
2. [整體架構](#2-整體架構)
3. [目錄結構](#3-目錄結構)
4. [資料模型](#4-資料模型)
5. [Backend Modules](#5-backend-modules)
   - 5.1 [RSS Fetcher](#51-rss-fetcher)
   - 5.2 [Deduplicator](#52-deduplicator)
   - 5.3 [AI Analyzer](#53-ai-analyzer)
   - 5.4 [Storage](#54-storage)
   - 5.5 [Email Notifier](#55-email-notifier)
   - 5.6 [Orchestrator](#56-orchestrator)
   - 5.7 [HTTP API](#57-http-api)
6. [Frontend Modules](#6-frontend-modules)
   - 6.1 [News List Page（首頁）](#61-news-list-page首頁)
   - 6.2 [History Page](#62-history-page)
   - 6.3 [Subscribe Page](#63-subscribe-page)
   - 6.4 [Shared Components](#64-shared-components)
7. [API 規格](#7-api-規格)
8. [Blob Storage 佈局](#8-blob-storage-佈局)
9. [環境變數](#9-環境變數)
10. [測試策略](#10-測試策略)
11. [部署架構](#11-部署架構)

---

## 1. 文件概覽

### 1.1 目的

本文件為台灣財經新聞每日彙整 App 的詳細設計規格，涵蓋各 module 的職責邊界、介面定義、資料模型、錯誤處理策略與可測試性設計。

### 1.2 技術決策摘要

| 項目 | 決策 |
|------|------|
| Backend 語言 | Python 3.13（uv 管理，本地開發）/ Azure Functions v4 |
| Frontend 框架 | Next.js（靜態匯出，部署至 Azure Static Web Apps） |
| AI 模型 | Gemini 2.0 Flash |
| 儲存 | Azure Blob Storage |
| Email | Azure Communication Services |
| 排程 | Azure Functions Timer Trigger（每天 01:00 UTC = 09:00 台灣時間） |

### 1.3 Module 列表

| # | Module | 層 | 職責 |
|---|--------|----|------|
| M1 | RSS Fetcher | Backend | 抓取各 RSS 來源原始文章 |
| M2 | Deduplicator | Backend | 跨來源標題相似度去重 |
| M3 | AI Analyzer | Backend | 呼叫 Gemini 進行篩選、分類、摘要、影響分析 |
| M4 | Storage | Backend | 讀寫 Azure Blob Storage |
| M5 | Email Notifier | Backend | 渲染 HTML Email 並透過 ACS 發送 |
| M6 | Orchestrator | Backend | 協調 M1–M5 的執行流程 |
| M7 | HTTP API | Backend | 提供 /api/news 與 /api/subscribe HTTP 端點 |
| M8 | News List Page | Frontend | 首頁，今日新聞卡片列表 |
| M9 | History Page | Frontend | 查看過去 7 天新聞 |
| M10 | Subscribe Page | Frontend | Email 訂閱表單 |
| M11 | Shared Components | Frontend | ArticleCard、CategorySection 等共用元件 |

---

## 2. 整體架構

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Functions（Python）                      │
│                                                                  │
│  [Timer Trigger 01:00 UTC]                                       │
│       │                                                          │
│       └─► Orchestrator (M6)                                      │
│               │                                                  │
│               ├─► RSS Fetcher (M1) ──► Deduplicator (M2)        │
│               │                              │                   │
│               │                        AI Analyzer (M3)         │
│               │                              │                   │
│               ├─► Storage (M4) ◄─────────────┘                  │
│               └─► Email Notifier (M5)                           │
│                                                                  │
│  [HTTP Trigger]                                                  │
│       ├─► GET  /api/news?date=YYYY-MM-DD  (M7)                  │
│       ├─► POST /api/subscribe             (M7)                  │
│       └─► GET  /api/unsubscribe?email=... (M7)                  │
└─────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
┌──────────────────┐         ┌────────────────────────────────┐
│  Azure Blob      │         │  Azure Static Web Apps         │
│  Storage         │◄──────► │  Next.js（靜態匯出）            │
│  news/           │         │                                │
│  subscribers/    │         │  /          今日新聞 (M8)       │
└──────────────────┘         │  /history   歷史新聞 (M9)       │
                             │  /subscribe 訂閱頁面 (M10)      │
                             └────────────────────────────────┘
```

### 2.1 資料流向

```
RSS Sources
    │  feedparser + httpx
    ▼
Raw Articles (List[RawArticle])
    │  標題相似度去重
    ▼
Deduplicated Articles (List[RawArticle])
    │  Gemini Flash API
    ▼
Analyzed Articles (DailyDigest JSON)
    │  Azure Blob Storage
    ▼
Blob: news/YYYY-MM-DD.json
    │                 │
    ▼                 ▼
HTTP API          Email Notifier
(前端查詢)        (HTML 寄送訂閱者)
```

---

## 3. 目錄結構

```
fin-news/
├── backend/                          # Azure Functions Python 應用
│   ├── function_app.py               # 主進入點，註冊所有 trigger
│   ├── fetcher/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py            # M1 主體
│   │   ├── sources.py                # RSS 來源設定
│   │   └── models.py                 # RawArticle dataclass
│   ├── deduplicator/
│   │   ├── __init__.py
│   │   └── deduplicator.py           # M2 主體
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── gemini_analyzer.py        # M3 主體
│   │   └── prompt_builder.py         # Gemini prompt 組裝
│   ├── storage/
│   │   ├── __init__.py
│   │   └── blob_storage.py           # M4 主體
│   ├── notifier/
│   │   ├── __init__.py
│   │   ├── email_notifier.py         # M5 主體
│   │   └── templates/
│   │       ├── daily_digest.html     # 每日摘要 HTML 模板
│   │       └── quota_exceeded.html   # Quota 超出通知模板
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── pipeline.py               # M6 主體
│   ├── api/
│   │   ├── __init__.py
│   │   ├── news_handler.py           # M7: GET /api/news
│   │   └── subscribe_handler.py      # M7: POST/GET /api/subscribe|unsubscribe
│   ├── tests/
│   │   ├── test_fetcher.py
│   │   ├── test_deduplicator.py
│   │   ├── test_analyzer.py
│   │   ├── test_storage.py
│   │   ├── test_notifier.py
│   │   ├── test_pipeline.py
│   │   └── test_api.py
│   └── host.json                     # Azure Functions 設定
├── frontend/                         # Next.js 應用
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # M8: 首頁
│   │   ├── history/
│   │   │   └── page.tsx              # M9
│   │   └── subscribe/
│   │       └── page.tsx              # M10
│   ├── components/
│   │   ├── ArticleCard.tsx           # M11
│   │   ├── CategorySection.tsx       # M11
│   │   ├── DatePicker.tsx            # M11
│   │   └── SubscribeForm.tsx         # M11
│   ├── lib/
│   │   └── api.ts                    # API 呼叫封裝
│   ├── types/
│   │   └── news.ts                   # TypeScript 型別
│   ├── next.config.ts
│   └── package.json
├── pyproject.toml                    # uv 管理
├── .env                              # 本地環境變數（不進 git）
└── .env.example                      # 環境變數範本
```

---

## 4. 資料模型

### 4.1 RawArticle（M1 輸出 / M2、M3 輸入）

```python
# backend/fetcher/models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RawArticle:
    title: str               # 文章標題
    url: str                 # 原文連結
    source: str              # 媒體名稱，例如 "經濟日報"
    published_at: datetime   # 發布時間（帶時區）
    description: str         # RSS 摘要（原始文字，非 AI 摘要）
```

### 4.2 AnalyzedArticle（M3 輸出 / M4、M5 輸入）

```python
@dataclass
class AnalyzedArticle:
    id: str                  # UUID，由 M3 生成
    title: str
    url: str
    source: str
    published_at: str        # ISO 8601 字串，帶時區
    category: str            # 四類之一，見 4.4
    summary: str             # AI 生成 2-3 段繁體中文摘要
    impact_analysis: str     # AI 生成對台灣市場的潛在影響分析
    sentiment: str           # "positive" | "negative" | "neutral"
```

### 4.3 DailyDigest（Blob Storage 存放格式 / API 回傳格式）

```json
{
  "date": "2026-05-16",
  "generated_at": "2026-05-16T09:05:00+08:00",
  "article_count": 12,
  "articles": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "台積電 Q2 法說會釋出樂觀展望，AI 需求超預期",
      "url": "https://money.udn.com/...",
      "source": "經濟日報",
      "published_at": "2026-05-16T08:30:00+08:00",
      "category": "科技股市",
      "summary": "台積電於 Q2 法說會上表示...",
      "impact_analysis": "• 正面影響：...\n• 關聯個股：...\n• 需注意：...",
      "sentiment": "positive"
    }
  ]
}
```

### 4.4 Category 枚舉

```python
class Category(str, Enum):
    TECH_MARKET = "科技股市"
    MACRO_ECONOMY = "總體經濟"
    LISTED_COMPANY = "上市公司公告"
    INTERNATIONAL = "國際財經"
```

### 4.5 Subscriber（Blob Storage 存放格式）

```json
[
  {
    "email": "user@example.com",
    "subscribed_at": "2026-05-16T09:00:00+08:00"
  }
]
```

---

## 5. Backend Modules

### 5.1 RSS Fetcher

**職責**：依設定抓取各 RSS 來源，回傳原始文章列表。單一來源失敗時不影響其他來源。

**介面**

```python
# backend/fetcher/rss_fetcher.py

def fetch_all_sources() -> list[RawArticle]:
    """
    抓取所有設定來源的 RSS Feed。
    單一來源失敗時記錄 warning 並跳過，不拋出例外。
    回傳：所有成功來源的文章合併列表（不去重）。
    """

def fetch_source(source: RSSSource) -> list[RawArticle]:
    """
    抓取單一 RSS 來源。
    失敗時拋出 FetchError。
    """
```

**RSS 來源設定**

```python
# backend/fetcher/sources.py

@dataclass
class RSSSource:
    name: str       # 媒體名稱
    url: str        # RSS Feed URL
    max_articles: int = 30  # 每次最多抓取數量

RSS_SOURCES: list[RSSSource] = [
    RSSSource("經濟日報",    "https://money.udn.com/rssfeed/news/1/1001?ch=money"),
    RSSSource("工商時報",    "https://ctee.com.tw/feed"),
    RSSSource("鉅亨網",      "https://feeds.cnyes.com/market/tw/news.xml"),
    RSSSource("MoneyDJ",    "https://www.moneydj.com/rss/news.aspx"),
    RSSSource("Yahoo財經",   "https://tw.news.yahoo.com/rss/finance"),
    RSSSource("科技新報",    "https://technews.tw/feed/"),
]
```

**錯誤處理**

| 情境 | 處理方式 |
|------|---------|
| HTTP 連線逾時（10 秒） | 記錄 `WARNING`，跳過此來源 |
| HTTP 非 200 狀態碼 | 記錄 `WARNING`，跳過此來源 |
| feedparser 解析失敗 | 記錄 `WARNING`，跳過此來源 |
| 所有來源皆失敗 | 記錄 `ERROR`，Orchestrator 終止當日任務 |

**依賴套件**：`feedparser`、`httpx`

**可測試性**：`fetch_source` 接受 `RSSSource` 物件，HTTP client 透過參數注入，可使用 `httpx.MockTransport` 在單元測試中模擬回應，不需真實網路。

---

### 5.2 Deduplicator

**職責**：對 `RawArticle` 列表進行跨來源去重，以標題字串相似度為判斷依據。

**介面**

```python
# backend/deduplicator/deduplicator.py

def deduplicate(articles: list[RawArticle], threshold: float = 0.8) -> list[RawArticle]:
    """
    移除標題相似度 >= threshold 的重複文章。
    若兩篇文章相似，保留 published_at 較早（即較早發布）的那篇。
    回傳：去重後的文章列表，順序依 published_at 由新至舊。

    Args:
        articles:  原始文章列表
        threshold: 相似度門檻，範圍 [0.0, 1.0]，預設 0.8
    """

def _similarity(a: str, b: str) -> float:
    """
    計算兩個標題字串的相似度，使用 difflib.SequenceMatcher。
    回傳：[0.0, 1.0]
    """
```

**演算法說明**

1. 對輸入列表以 `published_at` 由新到舊排序。
2. 採用 O(n²) 配對比較（預期 n ≤ 180，六來源各 30 則，效能可接受）。
3. 建立 `seen` 集合，對每篇新文章比較其標題與已接受文章的標題。
4. 若最大相似度 ≥ threshold，則略過此文章；否則加入 `seen`。

**可測試性**：純函數，無 I/O，直接以 `list[RawArticle]` 作為輸入進行單元測試。

---

### 5.3 AI Analyzer

**職責**：將去重後的文章批次送入 Gemini 2.0 Flash，取得篩選、分類、摘要、影響分析結果。

**介面**

```python
# backend/analyzer/gemini_analyzer.py

def analyze(articles: list[RawArticle]) -> list[AnalyzedArticle]:
    """
    呼叫 Gemini Flash API，回傳分析後的文章列表。
    Gemini 從輸入中選出 10-15 則最重要的文章。
    失敗時拋出 GeminiQuotaError 或 GeminiAPIError。
    """
```

**Prompt 設計**

```python
# backend/analyzer/prompt_builder.py

SYSTEM_PROMPT = """
你是一位台灣財經分析師。你的工作是從每日新聞中篩選重要資訊並提供分析。
輸出語言：繁體中文。
"""

def build_user_prompt(articles: list[RawArticle]) -> str:
    """
    組裝送入 Gemini 的 user prompt。
    格式：JSON 陣列，每則包含 title、source、url、published_at、description。
    指令內容：
      1. 從輸入中選出 10-15 則最重要的財經新聞
      2. 每則文章歸入四類：科技股市、總體經濟、上市公司公告、國際財經
      3. 每則生成 2-3 段繁體中文摘要
      4. 每則生成對台灣股市/科技業的潛在影響分析（含 sentiment: positive/negative/neutral）
      5. 以指定 JSON Schema 輸出，不要包含 markdown 程式碼區塊
    """
```

**Gemini 請求規格**

| 項目 | 值 |
|------|----|
| 模型 | `gemini-2.0-flash` |
| `response_mime_type` | `application/json` |
| `temperature` | `0.2`（降低隨機性，確保輸出格式穩定） |
| 每次請求文章數 | ≤ 180 則（feedparser 解析後的原始數量） |
| 逾時設定 | 60 秒 |

**錯誤處理**

| 情境 | 處理方式 |
|------|---------|
| HTTP 429（Quota 超過） | 拋出 `GeminiQuotaError`，由 Orchestrator 捕捉，觸發通知信 |
| HTTP 5xx / 連線失敗 | 重試最多 3 次（間隔 5 秒），仍失敗則拋出 `GeminiAPIError` |
| 回傳 JSON 格式無效 | 拋出 `GeminiResponseParseError` |

**可測試性**：Gemini client 透過依賴注入（constructor 注入或參數傳入），測試時傳入回傳 mock JSON 的假 client，無需真實 API 呼叫。

---

### 5.4 Storage

**職責**：封裝所有與 Azure Blob Storage 的讀寫操作，包含每日新聞 JSON 與訂閱者名單。

**介面**

```python
# backend/storage/blob_storage.py

class BlobStorageClient:

    def __init__(self, connection_string: str, container_name: str = "fin-news"):
        ...

    # --- 每日新聞 ---

    def save_daily_digest(self, digest: DailyDigest) -> None:
        """
        寫入 news/YYYY-MM-DD.json。
        若同日檔案已存在，覆蓋之。
        """

    def get_daily_digest(self, date: date) -> DailyDigest | None:
        """
        讀取指定日期的 JSON。
        不存在時回傳 None。
        """

    def list_available_dates(self) -> list[date]:
        """
        列出 news/ 前綴下所有 blob 對應的日期。
        回傳：由新至舊排序，最多 7 筆。
        """

    def cleanup_old_digests(self, keep_days: int = 7) -> int:
        """
        刪除超過 keep_days 天的 news/ blob。
        回傳：實際刪除的檔案數量。
        """

    # --- 訂閱者名單 ---

    def get_subscribers(self) -> list[Subscriber]:
        """
        讀取 subscribers/list.json。
        不存在時回傳空列表。
        """

    def add_subscriber(self, email: str) -> bool:
        """
        新增訂閱者。
        若 email 已存在，回傳 False（不重複新增）。
        若成功新增，回傳 True。
        使用樂觀鎖（ETag）避免並發寫入問題。
        """

    def remove_subscriber(self, email: str) -> bool:
        """
        移除訂閱者。
        若 email 不存在，回傳 False。
        若成功移除，回傳 True。
        """
```

**Blob 命名規則**

| 用途 | Blob 路徑 |
|------|----------|
| 每日新聞 | `news/2026-05-16.json` |
| 訂閱者名單 | `subscribers/list.json` |

**並發處理**：`add_subscriber` 與 `remove_subscriber` 使用 ETag 條件式寫入（`If-Match`），若發生並發衝突則重試最多 3 次。

**可測試性**：`BlobStorageClient` 可透過繼承一個 `AbstractStorageClient` 抽象類別實作，測試時使用 `InMemoryStorageClient` 替代，不需連接真實 Azure。

---

### 5.5 Email Notifier

**職責**：將每日新聞或異常通知渲染為 HTML Email，並透過 Azure Communication Services 寄出。

**介面**

```python
# backend/notifier/email_notifier.py

class EmailNotifier:

    def __init__(self, acs_connection_string: str, sender_address: str):
        ...

    def send_daily_digest(self, digest: DailyDigest, recipients: list[str]) -> SendResult:
        """
        渲染每日摘要 HTML，寄送給所有訂閱者。
        回傳：SendResult（成功數、失敗數）。
        """

    def send_quota_exceeded_notice(self, recipients: list[str]) -> SendResult:
        """
        寄出 Gemini API Quota 超過通知。
        內容：今日無法生成摘要，請直接查閱各財經媒體。
        """
```

**Email 內容規格（每日摘要）**

| 欄位 | 內容 |
|------|------|
| 主旨 | `📊 台灣財經日報 YYYY-MM-DD` |
| 寄件者 | 設定於環境變數 `ACS_SENDER_ADDRESS` |
| HTML 結構 | Header（日期）→ 依 Category 分組的文章列表 → 每篇含標題連結、摘要、影響分析 → Footer（退訂連結） |
| 退訂連結 | `{FRONTEND_URL}/api/unsubscribe?email={encoded_email}` |

**HTML 模板**（使用 Jinja2）

```
backend/notifier/templates/daily_digest.html  → 每日摘要
backend/notifier/templates/quota_exceeded.html → Quota 通知
```

**發送策略**：ACS 每次最多支援批次 `to` 欄位 50 個收件者。若訂閱者 > 50 人，分批發送。

**可測試性**：ACS client 透過建構子注入，測試時使用 mock client 驗證 HTML 渲染結果與呼叫參數，不實際發送 Email。

---

### 5.6 Orchestrator

**職責**：按序協調 M1–M5，實作完整的每日執行 pipeline。

**介面**

```python
# backend/orchestrator/pipeline.py

def run_daily_pipeline(
    storage: AbstractStorageClient,
    notifier: EmailNotifier,
    analyzer: GeminiAnalyzer,
) -> PipelineResult:
    """
    執行完整的每日新聞處理流程。
    回傳：PipelineResult（狀態、處理文章數、錯誤資訊）。
    """
```

**執行流程**

```
1. fetch_all_sources()
       │
       ├── 若所有來源失敗 → 記錄 ERROR，回傳 PipelineResult(status="failed")
       │
2. deduplicate(raw_articles)
       │
3. analyzer.analyze(deduped_articles)
       │
       ├── 若 GeminiQuotaError：
       │       └── 取得訂閱者列表 → send_quota_exceeded_notice() → 回傳 PipelineResult(status="quota_exceeded")
       │
       ├── 若 GeminiAPIError（重試後仍失敗）：
       │       └── 記錄 ERROR，回傳 PipelineResult(status="failed")
       │
4. storage.save_daily_digest(digest)
       │
5. storage.cleanup_old_digests(keep_days=7)
       │
6. recipients = storage.get_subscribers()
       │
       ├── 若 recipients 為空 → 略過發信
       │
7. notifier.send_daily_digest(digest, recipients)
       │
8. 回傳 PipelineResult(status="success", article_count=N)
```

**Azure Functions Timer Trigger 設定**

```python
# backend/function_app.py

@app.timer_trigger(
    schedule="0 0 1 * * *",   # 每天 01:00 UTC = 09:00 台灣時間
    arg_name="timer",
    run_on_startup=False,
)
def daily_pipeline_trigger(timer: func.TimerRequest) -> None:
    result = run_daily_pipeline(...)
    logging.info(f"Pipeline completed: {result}")
```

**可測試性**：`run_daily_pipeline` 所有依賴皆透過參數注入，測試時可傳入 mock 物件，完整驗證各步驟的呼叫與錯誤處理邏輯，不需觸發 Azure Functions。

---

### 5.7 HTTP API

**職責**：提供前端所需的 HTTP 端點。

#### GET /api/news

```python
# backend/api/news_handler.py

def handle_get_news(date_str: str | None, storage: AbstractStorageClient) -> HttpResponse:
    """
    查詢指定日期的新聞摘要。
    date_str 為 None 時，預設為今日（台灣時間）。
    """
```

| 情境 | HTTP 狀態 | 回傳 |
|------|-----------|------|
| 正常 | 200 | `DailyDigest` JSON |
| 日期格式錯誤 | 400 | `{"error": "invalid date format"}` |
| 指定日期無資料 | 404 | `{"error": "not found"}` |
| 日期超出 7 天範圍 | 400 | `{"error": "date out of range"}` |

#### POST /api/subscribe

```python
# backend/api/subscribe_handler.py

def handle_subscribe(body: dict, storage: AbstractStorageClient) -> HttpResponse:
    """
    新增訂閱者。
    body: {"email": "user@example.com"}
    """
```

| 情境 | HTTP 狀態 | 回傳 |
|------|-----------|------|
| 新增成功 | 201 | `{"message": "subscribed"}` |
| Email 已存在 | 200 | `{"message": "already subscribed"}` |
| Email 格式無效 | 400 | `{"error": "invalid email"}` |

#### GET /api/unsubscribe

```python
def handle_unsubscribe(email: str, storage: AbstractStorageClient) -> HttpResponse:
    """
    移除訂閱者（透過 Email 中的退訂連結觸發）。
    """
```

| 情境 | HTTP 狀態 | 回傳 |
|------|-----------|------|
| 移除成功 | 200 | `{"message": "unsubscribed"}` |
| Email 不存在 | 200 | `{"message": "not found"}` |

**CORS**：`function_app.py` 設定允許 Frontend URL 的跨域請求。

**Email 驗證規則**：使用 `email-validator` 套件，確保格式合法。

**可測試性**：handler function 接受 `storage` 參數，直接以 `InMemoryStorageClient` 進行單元測試，不需 HTTP server。

---

## 6. Frontend Modules

### 6.1 News List Page（首頁）

**路徑**：`/`  
**框架**：Next.js App Router，Client Component（`'use client'`）

**職責**：顯示今日新聞，依 Category 分組，支援點擊展開詳細分析。

**資料取得**

```typescript
// lib/api.ts
export async function fetchNews(date?: string): Promise<DailyDigest | null>
```

- 呼叫 `GET /api/news?date=YYYY-MM-DD`（或不帶 date 取得今日）
- 在 component mount 時呼叫，顯示 loading skeleton

**UI 結構**

```
<Header>          台灣財經日報  2026-05-16  [訂閱 Email]
<CategorySection> 科技股市
  <ArticleCard>   台積電 Q2 法說會...  [可展開]
    <ArticleDetail>（展開後顯示摘要 + 影響分析 + 原文連結）
<CategorySection> 總體經濟
  ...
```

**狀態管理**：每個 `ArticleCard` 維護自己的 `isExpanded: boolean` 狀態，不需全域 state。

**空狀態**：若 API 回傳 404，顯示「今日摘要尚未生成，請稍後再試」。

---

### 6.2 History Page

**路徑**：`/history`

**職責**：允許使用者選擇過去 7 天的日期，查看對應的新聞摘要。

**資料取得**

```typescript
// 頁面載入時
const dates = await fetchAvailableDates()  // GET /api/news/dates（回傳可用日期列表）
// 選擇日期時
const digest = await fetchNews(selectedDate)
```

> 注意：需在 M7 HTTP API 新增 `GET /api/news/dates` 端點，回傳 `string[]`（YYYY-MM-DD 格式），由 Storage 的 `list_available_dates()` 提供。

**UI 結構**

```
<DatePicker>  顯示過去 7 天，highlight 有資料的日期
<CategorySection + ArticleCard>  同首頁
```

---

### 6.3 Subscribe Page

**路徑**：`/subscribe`

**職責**：Email 訂閱表單。

**UI 結構**

```
<h1>訂閱台灣財經日報</h1>
<p>每天早上 09:00 收到財經摘要</p>
<SubscribeForm>
  <input type="email" placeholder="your@email.com" />
  <button>訂閱</button>
  <p>（訂閱後可隨時透過 Email 內退訂連結取消）</p>
```

**提交邏輯**

```typescript
async function handleSubmit(email: string) {
    const res = await fetch(`${API_BASE}/api/subscribe`, {
        method: 'POST',
        body: JSON.stringify({ email }),
        headers: { 'Content-Type': 'application/json' },
    })
    // 顯示成功或錯誤訊息
}
```

---

### 6.4 Shared Components

#### ArticleCard

```typescript
interface ArticleCardProps {
    article: AnalyzedArticle
}
```

- 收合狀態：顯示標題、來源、發布時間、sentiment badge
- 展開狀態：額外顯示摘要、影響分析（Markdown 渲染）、原文連結

#### CategorySection

```typescript
interface CategorySectionProps {
    category: string
    articles: AnalyzedArticle[]
}
```

#### DatePicker

```typescript
interface DatePickerProps {
    availableDates: string[]
    selectedDate: string
    onChange: (date: string) => void
}
```

#### SubscribeForm

處理表單狀態（idle / loading / success / error）與前端 email 格式驗證。

---

## 7. API 規格

### 7.1 端點列表

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/news` | 取得指定日期新聞（預設今日） |
| GET | `/api/news/dates` | 取得有資料的日期列表 |
| POST | `/api/subscribe` | 新增訂閱者 |
| GET | `/api/unsubscribe` | 移除訂閱者 |

### 7.2 GET /api/news

**Query Parameters**

| 參數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `date` | string | 否 | `YYYY-MM-DD` 格式，預設今日（台灣時間） |

**Response 200**

```json
{
  "date": "2026-05-16",
  "generated_at": "2026-05-16T09:05:00+08:00",
  "article_count": 12,
  "articles": [...]
}
```

### 7.3 GET /api/news/dates

**Response 200**

```json
{
  "dates": ["2026-05-16", "2026-05-15", "2026-05-14"]
}
```

### 7.4 POST /api/subscribe

**Request Body**

```json
{ "email": "user@example.com" }
```

### 7.5 GET /api/unsubscribe

**Query Parameters**

| 參數 | 型別 | 必填 |
|------|------|------|
| `email` | string | 是 |

---

## 8. Blob Storage 佈局

```
Container: fin-news
│
├── news/
│   ├── 2026-05-16.json     ← DailyDigest JSON（每日覆蓋）
│   ├── 2026-05-15.json
│   └── ...（最多保留 7 個）
│
└── subscribers/
    └── list.json           ← Subscriber[] JSON
```

**Container 存取層級**：Private（不開放公開匿名存取，只有 Azure Functions 透過連線字串存取）。

**清理機制**：每次 pipeline 執行完畢後，呼叫 `cleanup_old_digests(keep_days=7)`，刪除 8 天前的 blob。

---

## 9. 環境變數

```bash
# .env.example

# Gemini
GEMINI_API_KEY=

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=

# Azure Communication Services
ACS_CONNECTION_STRING=
ACS_SENDER_ADDRESS=                   # 例：noreply@yourdomain.com

# Frontend
NEXT_PUBLIC_API_BASE_URL=             # 例：https://your-function-app.azurewebsites.net

# （本地開發用）
AZURE_STORAGE_CONTAINER_NAME=fin-news
```

> `.env` 不進入版本控制。部署至 Azure 後，在 Function App 的「應用程式設定」中設定相同變數。

---

## 10. 測試策略

### 10.1 各 Module 測試範圍

| Module | 測試類型 | 關鍵測試案例 |
|--------|---------|------------|
| M1 RSS Fetcher | Unit | (1) 正常解析 RSS；(2) 單一來源 HTTP 失敗跳過；(3) 所有來源失敗回傳空列表 |
| M2 Deduplicator | Unit | (1) 完全相同標題；(2) 高相似度（≥0.8）去重；(3) 低相似度（<0.8）保留；(4) 空列表 |
| M3 AI Analyzer | Unit | (1) 正常解析 Gemini JSON 回應；(2) 429 → 拋出 GeminiQuotaError；(3) 回傳無效 JSON → 拋出 GeminiResponseParseError |
| M4 Storage | Unit | (1) save/get 每日 JSON；(2) add_subscriber 不重複；(3) remove_subscriber；(4) cleanup 刪除超過 7 天 |
| M5 Email Notifier | Unit | (1) HTML 渲染包含所有文章；(2) 退訂連結正確；(3) 訂閱者 > 50 時分批發送 |
| M6 Orchestrator | Integration | (1) 正常流程端對端；(2) RSS 全失敗終止；(3) Quota exceeded → 通知 |
| M7 HTTP API | Unit | 各端點的 200/400/404 回應 |

### 10.2 測試工具

| 工具 | 用途 |
|------|------|
| `pytest` | 測試框架（已在 pyproject.toml） |
| `pytest-asyncio` | 非同步函數測試 |
| `httpx.MockTransport` | M1 HTTP 請求模擬 |
| `unittest.mock.MagicMock` | M3 Gemini client mock、M5 ACS client mock |
| `InMemoryStorageClient` | M4 的測試替身（實作 AbstractStorageClient） |

### 10.3 執行方式

```bash
# 在專案根目錄
uv run pytest backend/tests/ -v

# 單一 module
uv run pytest backend/tests/test_deduplicator.py -v

# 含覆蓋率
uv run pytest backend/tests/ --cov=backend --cov-report=term-missing
```

---

## 11. 部署架構

### 11.1 資源對應

| 資源 | 用途 | 方案 |
|------|------|------|
| Azure Functions | Timer Trigger（pipeline）+ HTTP Triggers（API） | Consumption |
| Azure Blob Storage | 新聞 JSON + 訂閱者名單 | LRS |
| Azure Static Web Apps | Next.js 靜態匯出前端 | Free |
| Azure Communication Services | Email 寄送 | 免費 100 封/天 |

### 11.2 Python 版本注意事項

本地開發使用 Python 3.13（uv）。Azure Functions v4 目前對 Python 3.11 支援最完整，3.13 支援狀態需在建立 Function App 時確認。**建議**：先在 Azure Portal 確認可用的 Python 版本，若 3.13 不支援，Azure Functions 部署環境使用 3.11，本地開發維持 3.13（兩版本語法相容）。

### 11.3 Next.js 部署

使用 `next build` + 靜態匯出模式（`output: 'export'`）產生純靜態檔案，部署至 Azure Static Web Apps。`NEXT_PUBLIC_API_BASE_URL` 設定為 Azure Functions 的 URL。

### 11.4 CI/CD（後續）

建議使用 GitHub Actions，分兩個 workflow：
- `backend.yml`：執行 pytest，部署 Azure Functions
- `frontend.yml`：執行 `next build`，部署 Azure Static Web Apps

---

*本設計文件完成後，依 Phase 1–6 順序開始實作。*
