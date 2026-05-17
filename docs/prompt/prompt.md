# 台灣財經新聞每日彙整 App — Vibe Coding 起始 Prompt

> 將此文件內容完整貼入 Cursor Agent 作為起始 prompt。
> 整個開發過程不需要任何人工介入。

---

## 你的角色：主 Agent（Master Orchestrator）

你是這個專案的主 Agent，負責以下四件事：

1. 閱讀設計文件，完整理解整體架構
2. 依照任務依賴關係，有序派發子 Agent 實作各 module
3. 驗證每個 module 的品質門檻後才推進下一步
4. 實時更新 `docs/tasks/progress.md` 的進度 checkbox

**全程不需等待人工確認。遇到設計文件未明確說明之處，自行做出合理判斷並繼續執行。**

---

## 專案概覽

**工作目錄**：`/Users/harryp/Desktop/Projects/Fin-News`

**專案目標**：建立自動化系統，每天早上 09:00（台灣時間）抓取台灣財經新聞，透過 Gemini 2.0 Flash 進行 AI 摘要與影響分析，以網頁及 Email 訂閱兩種方式呈現。

**技術棧**：

| 層 | 技術 |
|----|------|
| Backend 語言 | Python 3.13（uv 管理）/ Azure Functions v4 |
| Frontend | Next.js App Router + TypeScript + Tailwind CSS（靜態匯出） |
| AI | Gemini 2.0 Flash（`gemini-2.0-flash`） |
| 儲存 | Azure Blob Storage（Container: `fin-news`） |
| Email | Azure Communication Services |
| 排程 | Azure Functions Timer Trigger（每天 01:00 UTC = 09:00 台灣時間） |

**關鍵文件**（開始前必須全部閱讀）：

- `docs/proposal.md` — 專案需求與目標
- `docs/detailed-design.md` — 完整架構、介面定義、資料模型、錯誤處理
- `docs/tasks/progress.md` — 整體進度追蹤與任務列表
- `docs/tasks/m0-project-setup.md` 到 `docs/tasks/m11-shared-components.md` — 各 module 詳細任務

**環境變數**（已設定於 `.env`，本地開發使用，測試時不得依賴）：

```bash
GEMINI_API_KEY=...
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER_NAME=fin-news
ACS_CONNECTION_STRING=...
ACS_SENDER_ADDRESS=DoNotReply@...azurecomm.net
NEXT_PUBLIC_API_BASE_URL=https://...azurewebsites.net
```

---

## 品質標準（Quality Gates）

**每個 module 的子 Agent 必須在回報完成前，確認以下對應的全部指令輸出無錯誤。**

### Backend（Python）

```bash
# 在專案根目錄執行
uv run pytest backend/tests/test_<module_name>.py -v
uv run mypy backend/<module_dir>/ --ignore-missing-imports
uv run ruff check backend/<module_dir>/
uv run ruff format --check backend/<module_dir>/
```

規則：
- 測試覆蓋率須涵蓋設計文件 `docs/detailed-design.md` Section 10 所有列出的測試案例
- 禁止使用 `# type: ignore` 或 `# noqa`（除非有明確技術原因，必須加行內說明）
- **所有測試使用 mock，不呼叫真實外部服務**（Gemini API、Azure Blob、ACS Email）

### Frontend（TypeScript / Next.js）

```bash
# 在 frontend/ 目錄執行
npx tsc --noEmit
npx eslint . --max-warnings 0
npx vitest run
```

規則：
- 每個 React 元件必須有對應的 Vitest 單元測試
- 測試使用 `@testing-library/react` + `vitest`，mock 所有 API 呼叫
- TypeScript strict 模式，無 `any` 類型
- **禁止使用 `// @ts-ignore` 或 `// eslint-disable`**

---

## 執行流程

### Step 1：初始化（閱讀文件）

在派發任何子 Agent 之前，主 Agent 必須自行：

1. 閱讀 `docs/proposal.md`
2. 閱讀 `docs/detailed-design.md`（完整，1001 行）
3. 閱讀 `docs/tasks/progress.md` 確認初始狀態
4. 逐一閱讀 `docs/tasks/m0-project-setup.md` 到 `docs/tasks/m11-shared-components.md`

目的：確保主 Agent 對整體架構有完整理解，能夠驗證子 Agent 的產出是否符合設計。

---

### Step 2：M0 — Project Setup（必須最先完成）

派發子 Agent 完成 M0。子 Agent 指令如下：

```
你是 M0 Project Setup 的實作 Agent。

任務文件：docs/tasks/m0-project-setup.md
設計文件參考：docs/detailed-design.md Section 3（目錄結構）

你需要完成以下 6 項任務：

T0-1：建立 backend/ 目錄骨架
  建立以下所有目錄與 __init__.py：
  backend/fetcher/、backend/deduplicator/、backend/analyzer/
  backend/storage/、backend/notifier/templates/、backend/orchestrator/
  backend/api/、backend/tests/

T0-2：建立 pyproject.toml（uv 管理）
  [project]
  name = "fin-news-backend"
  requires-python = ">=3.11"
  dependencies = [
      "azure-functions",
      "azure-storage-blob",
      "azure-communication-email",
      "feedparser",
      "httpx",
      "google-generativeai",
      "jinja2",
      "email-validator",
  ]
  [project.optional-dependencies]
  dev = [
      "pytest",
      "pytest-asyncio",
      "pytest-cov",
      "mypy",
      "ruff",
  ]
  執行 uv sync 安裝依賴。

T0-3：建立 backend/host.json
  {
    "version": "2.0",
    "logging": { "applicationInsights": { "samplingSettings": { "isEnabled": true, "excludedTypes": "Request" } } },
    "extensionBundle": { "id": "Microsoft.Azure.Functions.ExtensionBundle", "version": "[4.*, 5.0.0)" }
  }

T0-4：初始化 Next.js 前端專案
  在 frontend/ 目錄執行：
  npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*" --yes
  在 next.config.ts 加入 output: 'export'
  安裝測試依賴：npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
  建立 vitest.config.ts（使用 jsdom 環境）
  在 package.json scripts 加入 "test": "vitest run"

T0-5：建立 .env.example
  GEMINI_API_KEY=
  AZURE_STORAGE_CONNECTION_STRING=
  AZURE_STORAGE_CONTAINER_NAME=fin-news
  ACS_CONNECTION_STRING=
  ACS_SENDER_ADDRESS=
  NEXT_PUBLIC_API_BASE_URL=http://localhost:7071
  確認 .gitignore 包含 .env

T0-6：建立 backend/function_app.py 骨架
  import azure.functions as func
  app = func.FunctionApp()

驗收標準：
- uv run python -c "import backend" 不報錯
- cd frontend && npm run build 成功產出 out/
- uv run pytest --version 可執行

完成後列出所有建立的檔案路徑。
```

M0 子 Agent 完成後，主 Agent：
1. 驗收上述驗收標準是否通過
2. 將 `docs/tasks/progress.md` 中 M0 的 6 個 `- [ ]` 全部改為 `- [x]`，狀態改為 ✅

---

### Step 3：並行開發（Backend 線 + Frontend 線）

M0 完成後，**同時**派發兩個子 Agent 起始點：
- Backend：派發 **M1 RSS Fetcher** 子 Agent
- Frontend：派發 **M11 Shared Components** 子 Agent

兩條線**各自獨立**，互不等待（除非有明確依賴）。

---

## Backend 開發順序與子 Agent 指令模板

### 依賴鏈

```
M1（RSS Fetcher）→ M2（Deduplicator）→ M3（AI Analyzer）→ M4（Storage）→ M5（Email Notifier）→ M6（Orchestrator）
                                                                          └─► M7（HTTP API）
```

M4 完成後，M5 與 M7 可並行。M5 完成後才能做 M6。

---

### M1 — RSS Fetcher

```
你是 M1 RSS Fetcher 的實作 Agent。

任務文件：docs/tasks/m1-rss-fetcher.md
設計文件參考：docs/detailed-design.md Section 5.1

實作以下檔案：
- backend/fetcher/models.py     → RawArticle dataclass
- backend/fetcher/sources.py    → RSSSource dataclass + RSS_SOURCES（6 個來源）
- backend/fetcher/exceptions.py → FetchError
- backend/fetcher/rss_fetcher.py → fetch_source() + fetch_all_sources()
- backend/fetcher/__init__.py
- backend/tests/test_fetcher.py → 5 個測試案例（詳見任務文件）

關鍵實作細節：
- fetch_source() 使用 httpx.Client（可注入），timeout=10 秒
- 解析 feedparser entry 的 published_parsed / updated_parsed → datetime（帶 UTC 時區）
- HTTP 非 200 或解析失敗 → 拋出 FetchError
- fetch_all_sources() 捕捉 FetchError，logging.warning()，繼續其他來源
- 所有來源失敗 → logging.error()，回傳 []

測試使用 httpx.MockTransport 模擬 HTTP 回應，不發出真實網路請求。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_fetcher.py -v
uv run mypy backend/fetcher/ --ignore-missing-imports
uv run ruff check backend/fetcher/
uv run ruff format --check backend/fetcher/

完成後回報：所有品質檢查的輸出結果。
```

---

### M2 — Deduplicator

```
你是 M2 Deduplicator 的實作 Agent。

任務文件：docs/tasks/m2-deduplicator.md
設計文件參考：docs/detailed-design.md Section 5.2
前置依賴：M1 已完成，RawArticle 可從 backend/fetcher/models.py import

實作以下檔案：
- backend/deduplicator/deduplicator.py → _similarity() + deduplicate()
- backend/deduplicator/__init__.py
- backend/tests/test_deduplicator.py   → 7 個測試案例（詳見任務文件）

演算法：
1. 輸入列表按 published_at 由新至舊排序
2. 對每篇文章，計算其標題與 accepted 列表中所有文章的相似度
3. 最大相似度 >= threshold（預設 0.8）→ 略過
4. 否則加入 accepted
5. 回傳 accepted（已由新至舊排序）

_similarity() 使用 difflib.SequenceMatcher，純函數，無 I/O。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_deduplicator.py -v
uv run mypy backend/deduplicator/ --ignore-missing-imports
uv run ruff check backend/deduplicator/
uv run ruff format --check backend/deduplicator/

完成後回報：所有品質檢查的輸出結果。
```

---

### M3 — AI Analyzer

```
你是 M3 AI Analyzer 的實作 Agent。

任務文件：docs/tasks/m3-ai-analyzer.md
設計文件參考：docs/detailed-design.md Section 5.3
前置依賴：M1 已完成

實作以下檔案：
- backend/analyzer/models.py         → Category(Enum) + AnalyzedArticle dataclass
- backend/analyzer/exceptions.py     → GeminiQuotaError、GeminiAPIError、GeminiResponseParseError
- backend/analyzer/prompt_builder.py → SYSTEM_PROMPT + OUTPUT_SCHEMA + build_user_prompt()
- backend/analyzer/gemini_analyzer.py → GeminiAnalyzer 類別
- backend/analyzer/__init__.py
- backend/tests/test_analyzer.py     → 5 個測試案例（詳見任務文件）

GeminiAnalyzer 規格：
- __init__(self, api_key: str, client=None)：client 為依賴注入，測試時傳入 mock
- 使用 google-generativeai SDK，模型 gemini-2.0-flash
- response_mime_type="application/json"，temperature=0.2
- HTTP 429 → GeminiQuotaError（不重試）
- HTTP 5xx / 連線失敗 → 重試最多 3 次（間隔 5 秒），仍失敗 → GeminiAPIError
- JSON 解析失敗 → GeminiResponseParseError
- 成功後為每篇文章生成 UUID id，組裝 list[AnalyzedArticle]

所有測試使用 unittest.mock.MagicMock 模擬 Gemini client，不呼叫真實 API。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_analyzer.py -v
uv run mypy backend/analyzer/ --ignore-missing-imports
uv run ruff check backend/analyzer/
uv run ruff format --check backend/analyzer/

完成後回報：所有品質檢查的輸出結果。
```

---

### M4 — Storage

```
你是 M4 Storage 的實作 Agent。

任務文件：docs/tasks/m4-storage.md
設計文件參考：docs/detailed-design.md Section 5.4、4.3、4.5、8
前置依賴：M3 已完成（需要 AnalyzedArticle）

實作以下檔案：
- backend/storage/models.py           → DailyDigest dataclass + Subscriber dataclass（含 JSON 序列化方法）
- backend/storage/abstract_storage.py → AbstractStorageClient 抽象基礎類別（ABC）
- backend/storage/in_memory_storage.py → InMemoryStorageClient（測試替身，實作 AbstractStorageClient）
- backend/storage/blob_storage.py     → BlobStorageClient（實作 AbstractStorageClient）
- backend/storage/__init__.py
- backend/tests/test_storage.py       → 測試案例（詳見任務文件）

AbstractStorageClient 定義以下抽象方法：
- save_daily_digest(digest: DailyDigest) -> None
- get_daily_digest(date: date) -> DailyDigest | None
- list_available_dates() -> list[date]
- cleanup_old_digests(keep_days: int = 7) -> int
- get_subscribers() -> list[Subscriber]
- add_subscriber(email: str) -> bool
- remove_subscriber(email: str) -> bool

InMemoryStorageClient 用於測試，以 dict 模擬 Blob Storage。

BlobStorageClient：
- Blob 路徑：news/YYYY-MM-DD.json、subscribers/list.json
- add_subscriber 與 remove_subscriber 使用 ETag 條件式寫入，衝突時重試最多 3 次
- 測試使用 InMemoryStorageClient，不測試真實 BlobStorageClient（避免依賴 Azure）

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_storage.py -v
uv run mypy backend/storage/ --ignore-missing-imports
uv run ruff check backend/storage/
uv run ruff format --check backend/storage/

完成後回報：所有品質檢查的輸出結果。
```

---

### M5 — Email Notifier

```
你是 M5 Email Notifier 的實作 Agent。

任務文件：docs/tasks/m5-email-notifier.md
設計文件參考：docs/detailed-design.md Section 5.5
前置依賴：M4 已完成（需要 DailyDigest）

實作以下檔案：
- backend/notifier/templates/daily_digest.html   → Jinja2 HTML Email 模板（每日摘要）
- backend/notifier/templates/quota_exceeded.html → Jinja2 HTML Email 模板（Quota 通知）
- backend/notifier/email_notifier.py             → SendResult dataclass + EmailNotifier 類別
- backend/notifier/__init__.py
- backend/tests/test_notifier.py                 → 測試案例（詳見任務文件）

EmailNotifier 規格：
- __init__(self, acs_connection_string: str, sender_address: str, client=None)
- send_daily_digest(digest, recipients) → SendResult：渲染 daily_digest.html 寄送，訂閱者 > 50 時分批
- send_quota_exceeded_notice(recipients) → SendResult：渲染 quota_exceeded.html 寄送
- 每批最多 50 個收件者（ACS 限制）

Email 主旨格式：📊 台灣財經日報 YYYY-MM-DD
退訂連結格式：{NEXT_PUBLIC_API_BASE_URL}/api/unsubscribe?email={url_encoded_email}

HTML 模板使用 Jinja2，依 Category 分組文章，每篇含標題連結、摘要、影響分析、情緒標記。

所有測試使用 MagicMock 模擬 ACS client，驗證 HTML 渲染內容與呼叫參數。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_notifier.py -v
uv run mypy backend/notifier/ --ignore-missing-imports
uv run ruff check backend/notifier/
uv run ruff format --check backend/notifier/

完成後回報：所有品質檢查的輸出結果。
```

---

### M6 — Orchestrator

```
你是 M6 Orchestrator 的實作 Agent。

任務文件：docs/tasks/m6-orchestrator.md
設計文件參考：docs/detailed-design.md Section 5.6
前置依賴：M1、M2、M3、M4、M5 全部完成

實作以下檔案：
- backend/orchestrator/models.py  → PipelineResult dataclass（status: "success"|"failed"|"quota_exceeded"）
- backend/orchestrator/pipeline.py → run_daily_pipeline() 函式
- backend/orchestrator/__init__.py
- backend/function_app.py         → 更新為完整版本（含 Timer Trigger 註冊）
- backend/tests/test_pipeline.py  → 6 個整合測試案例（詳見任務文件）

run_daily_pipeline(storage, notifier, analyzer) 執行流程：
Step 1: fetch_all_sources() → 若空 → return PipelineResult(status="failed")
Step 2: deduplicate(raw_articles) → log INFO 去重結果
Step 3: analyzer.analyze(deduped)
        GeminiQuotaError → send_quota_exceeded_notice → return PipelineResult(status="quota_exceeded")
        GeminiAPIError → log ERROR → return PipelineResult(status="failed")
Step 4: storage.save_daily_digest(digest)
Step 5: storage.cleanup_old_digests(keep_days=7)
Step 6: 若有訂閱者 → notifier.send_daily_digest(...)
Step 7: return PipelineResult(status="success", article_count=N)

Timer Trigger cron：0 0 1 * * *（每天 01:00 UTC）

測試使用 InMemoryStorageClient + MagicMock，完整覆蓋各分支。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_pipeline.py -v
uv run mypy backend/orchestrator/ --ignore-missing-imports
uv run ruff check backend/orchestrator/
uv run ruff format --check backend/orchestrator/

完成後回報：所有品質檢查的輸出結果。
```

---

### M7 — HTTP API

```
你是 M7 HTTP API 的實作 Agent。

任務文件：docs/tasks/m7-http-api.md
設計文件參考：docs/detailed-design.md Section 5.7、7
前置依賴：M4 已完成（需要 AbstractStorageClient）

實作以下檔案：
- backend/api/news_handler.py       → handle_get_news() + handle_get_news_dates()
- backend/api/subscribe_handler.py  → handle_subscribe() + handle_unsubscribe()
- backend/api/__init__.py
- backend/function_app.py           → 在既有 Timer Trigger 基礎上追加 HTTP Trigger 路由
- backend/tests/test_api.py         → 各端點 200/400/404 測試案例

端點規格：
GET  /api/news?date=YYYY-MM-DD → DailyDigest JSON | 400 | 404
GET  /api/news/dates           → {"dates": ["YYYY-MM-DD", ...]}
POST /api/subscribe            → body: {"email": "..."} → 201 | 200 | 400
GET  /api/unsubscribe?email=.. → 200（成功或不存在皆 200）

Email 格式驗證使用 email-validator 套件。
日期超出 7 天範圍 → 400 {"error": "date out of range"}
CORS 設定允許 NEXT_PUBLIC_API_BASE_URL。

所有 handler 接受 storage 參數注入，測試使用 InMemoryStorageClient。

品質檢查（必須全部通過）：
uv run pytest backend/tests/test_api.py -v
uv run mypy backend/api/ --ignore-missing-imports
uv run ruff check backend/api/
uv run ruff format --check backend/api/

完成後回報：所有品質檢查的輸出結果。
```

---

## Frontend 開發順序與子 Agent 指令模板

### 依賴鏈

```
M11（Shared Components）
  ├─► M8（News List Page）
  ├─► M9（History Page）
  └─► M10（Subscribe Page）
```

M11 完成後，M8、M9、M10 可並行。

---

### M11 — Shared Components

```
你是 M11 Shared Components 的實作 Agent。

任務文件：docs/tasks/m11-shared-components.md
設計文件參考：docs/detailed-design.md Section 6.4、4.2、4.3
工作目錄：frontend/

實作以下檔案：
- frontend/types/news.ts              → TypeScript 型別定義（對應 detailed-design.md Section 4）
- frontend/lib/api.ts                 → fetchNews() + fetchAvailableDates() + subscribeEmail()
- frontend/components/ArticleCard.tsx → 展開/收合 + sentiment badge + Markdown 渲染
- frontend/components/CategorySection.tsx → 空列表不渲染
- frontend/components/DatePicker.tsx  → 日期 highlight + 空狀態
- frontend/components/SubscribeForm.tsx → 狀態機（idle/loading/success/error）+ 前端 email 驗證
- frontend/components/__tests__/ArticleCard.test.tsx
- frontend/components/__tests__/CategorySection.test.tsx
- frontend/components/__tests__/DatePicker.test.tsx
- frontend/components/__tests__/SubscribeForm.test.tsx

TypeScript 型別（對應後端資料模型）：
interface AnalyzedArticle {
  id: string; title: string; url: string; source: string;
  published_at: string; category: string; summary: string;
  impact_analysis: string; sentiment: "positive" | "negative" | "neutral";
}
interface DailyDigest {
  date: string; generated_at: string; article_count: number; articles: AnalyzedArticle[];
}
interface Subscriber { email: string; subscribed_at: string; }

API base URL 從環境變數 NEXT_PUBLIC_API_BASE_URL 讀取。

所有元件測試使用 @testing-library/react + vitest，mock fetch() 呼叫。

品質檢查（在 frontend/ 目錄執行，必須全部通過）：
npx tsc --noEmit
npx eslint . --max-warnings 0
npx vitest run

完成後回報：所有品質檢查的輸出結果。
```

---

### M8 — News List Page

```
你是 M8 News List Page 的實作 Agent。

任務文件：docs/tasks/m8-news-list-page.md
設計文件參考：docs/detailed-design.md Section 6.1
前置依賴：M11 已完成
工作目錄：frontend/

實作以下檔案：
- frontend/app/layout.tsx → 全域佈局（Header + Footer + 字型 + Tailwind）
- frontend/app/page.tsx   → 首頁（'use client'，loading/empty/content 三種狀態）
- frontend/components/LoadingSkeleton.tsx → 載入骨架屏
- frontend/app/__tests__/page.test.tsx → 首頁測試

首頁規格：
- mount 時呼叫 fetchNews()（無 date 參數 = 今日）
- 顯示 loading skeleton 直到資料就緒
- API 404 → 顯示「今日摘要尚未生成，請稍後再試」
- 資料就緒 → 使用 CategorySection + ArticleCard 分組顯示
- Header 包含：標題「台灣財經日報」、日期、[訂閱 Email] 按鈕（連結 /subscribe）

品質檢查（在 frontend/ 目錄執行，必須全部通過）：
npx tsc --noEmit
npx eslint . --max-warnings 0
npx vitest run

完成後回報：所有品質檢查的輸出結果。
```

---

### M9 — History Page

```
你是 M9 History Page 的實作 Agent。

任務文件：docs/tasks/m9-history-page.md
設計文件參考：docs/detailed-design.md Section 6.2
前置依賴：M11 已完成
工作目錄：frontend/

實作以下檔案：
- frontend/app/history/page.tsx → 歷史新聞頁面
- frontend/app/history/__tests__/page.test.tsx

頁面規格：
- 載入時呼叫 fetchAvailableDates()，取得有資料的日期列表
- 使用 DatePicker 顯示日期選擇器，有資料的日期 highlight
- 選擇日期後呼叫 fetchNews(selectedDate)，渲染 CategorySection + ArticleCard
- 預設選中最新可用日期

品質檢查（在 frontend/ 目錄執行，必須全部通過）：
npx tsc --noEmit
npx eslint . --max-warnings 0
npx vitest run

完成後回報：所有品質檢查的輸出結果。
```

---

### M10 — Subscribe Page

```
你是 M10 Subscribe Page 的實作 Agent。

任務文件：docs/tasks/m10-subscribe-page.md
設計文件參考：docs/detailed-design.md Section 6.3
前置依賴：M11 已完成
工作目錄：frontend/

實作以下檔案：
- frontend/app/subscribe/page.tsx → 訂閱頁面
- frontend/app/subscribe/__tests__/page.test.tsx

頁面規格：
- 使用 SubscribeForm 元件
- 成功訂閱後顯示確認訊息
- 已訂閱的 email → 顯示「您已訂閱」
- 包含說明文字「每天早上 09:00 收到財經摘要」

品質檢查（在 frontend/ 目錄執行，必須全部通過）：
npx tsc --noEmit
npx eslint . --max-warnings 0
npx vitest run

完成後回報：所有品質檢查的輸出結果。
```

---

## 進度追蹤規則

每當一個 module 的子 Agent 回報完成，主 Agent 必須：

1. 驗證品質檢查輸出（所有指令必須 exit code 0，無錯誤/警告）
2. 若有品質問題：重新派發該子 Agent，要求修正後再回報
3. 驗收通過後：開啟 `docs/tasks/progress.md`，將該 module 的所有 `- [ ]` 改為 `- [x]`，表格狀態改為 ✅，「完成」數字更新為實際任務數

**進度更新格式範例**：

```markdown
| M1 RSS Fetcher | Backend | 6 | 6 | ✅ 完成 |
```

---

## 最終驗收

所有 module（M0-M11）完成後，主 Agent 執行全域品質檢查：

```bash
# Backend 全域
uv run pytest backend/tests/ -v --cov=backend --cov-report=term-missing
uv run mypy backend/ --ignore-missing-imports
uv run ruff check backend/
uv run ruff format --check backend/

# Frontend 全域
cd frontend && npx tsc --noEmit && npx eslint . --max-warnings 0 && npx vitest run
```

若全部通過：開發完成，在 `docs/tasks/progress.md` 最頂部加入完成時間戳記。

若有失敗：定位失敗的 module，重新派發對應子 Agent 修正。

---

## 開始執行

請按以下順序立即開始，不需等待人工確認：

1. 閱讀 `docs/proposal.md`、`docs/detailed-design.md`、所有 `docs/tasks/*.md`
2. 確認工作目錄為 `/Users/harryp/Desktop/Projects/Fin-News`
3. 派發 M0 Project Setup 子 Agent
4. M0 完成後，**同時**派發 M1（Backend 線）與 M11（Frontend 線）的子 Agent
5. 依照依賴鏈，每個 module 完成後自動派發下一個
6. 持續更新 `docs/tasks/progress.md`
7. 全部完成後執行最終驗收

**現在開始。**
