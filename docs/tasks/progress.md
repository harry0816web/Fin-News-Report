# 台灣財經新聞 App — 整體開發進度

> ✅ **全部完成：2026-05-17 10:52（UTC+8）**  
> Backend 53 tests passed｜Frontend 23 tests passed｜mypy 0 issues｜ruff clean｜tsc 0 errors｜ESLint 0 warnings  
> 最後更新：2026-05-17  
> 總任務數：51 項｜已完成：51 項

---

## 整體進度概覽

| Module | 層 | 任務數 | 完成 | 狀態 |
|--------|----|--------|------|------|
| M0 Project Setup | — | 6 | 6 | ✅ 完成 |
| M1 RSS Fetcher | Backend | 6 | 6 | ✅ 完成 |
| M2 Deduplicator | Backend | 3 | 3 | ✅ 完成 |
| M3 AI Analyzer | Backend | 5 | 5 | ✅ 完成 |
| M4 Storage | Backend | 5 | 5 | ✅ 完成 |
| M5 Email Notifier | Backend | 5 | 5 | ✅ 完成 |
| M6 Orchestrator | Backend | 4 | 4 | ✅ 完成 |
| M7 HTTP API | Backend | 6 | 6 | ✅ 完成 |
| M8 News List Page | Frontend | 5 | 5 | ✅ 完成 |
| M9 History Page | Frontend | 2 | 2 | ✅ 完成 |
| M10 Subscribe Page | Frontend | 2 | 2 | ✅ 完成 |
| M11 Shared Components | Frontend | 4 | 4 | ✅ 完成 |

---

## M0 — Project Setup

- [x] T0-1 建立 backend/ 目錄骨架
- [x] T0-2 安裝 Python 依賴套件（`uv sync`）
- [x] T0-3 建立 `host.json`
- [x] T0-4 初始化 Next.js 前端專案
- [x] T0-5 建立 `.env.example` 與 `.gitignore`
- [x] T0-6 建立 `function_app.py` 骨架

---

## M1 — RSS Fetcher

- [x] T1-1 `RawArticle` dataclass（`backend/fetcher/models.py`）
- [x] T1-2 `RSSSource` 與 `RSS_SOURCES`（`backend/fetcher/sources.py`）
- [x] T1-3 `FetchError` 例外（`backend/fetcher/exceptions.py`）
- [x] T1-4 `fetch_source()` 實作
- [x] T1-5 `fetch_all_sources()` 實作
- [x] T1-6 單元測試全通過（`test_fetcher.py`）

---

## M2 — Deduplicator

- [x] T2-1 `_similarity()` 實作
- [x] T2-2 `deduplicate()` 實作
- [x] T2-3 單元測試全通過（`test_deduplicator.py`）

---

## M3 — AI Analyzer

- [x] T3-1 `AnalyzedArticle` 與 `Category` 定義（`backend/analyzer/models.py`）
- [x] T3-2 三種例外定義（`GeminiQuotaError`、`GeminiAPIError`、`GeminiResponseParseError`）
- [x] T3-3 `build_user_prompt()` 實作
- [x] T3-4 `GeminiAnalyzer.analyze()` 實作（含重試邏輯）
- [x] T3-5 單元測試全通過（`test_analyzer.py`）

---

## M4 — Storage

- [x] T4-1 `DailyDigest` 與 `Subscriber` 定義（含序列化方法）
- [x] T4-2 `AbstractStorageClient` 抽象類別定義
- [x] T4-3 `InMemoryStorageClient` 實作（測試替身）
- [x] T4-4 `BlobStorageClient` 實作
- [x] T4-5 單元測試全通過（`test_storage.py`）

---

## M5 — Email Notifier

- [x] T5-1 `daily_digest.html` Jinja2 模板
- [x] T5-2 `quota_exceeded.html` Jinja2 模板
- [x] T5-3 `SendResult` dataclass 定義
- [x] T5-4 `EmailNotifier` 實作（含分批發送 ≤50）
- [x] T5-5 單元測試全通過（`test_notifier.py`）

---

## M6 — Orchestrator

- [x] T6-1 `PipelineResult` dataclass 定義
- [x] T6-2 `run_daily_pipeline()` 實作（完整 pipeline 流程）
- [x] T6-3 Timer Trigger 在 `function_app.py` 註冊
- [x] T6-4 整合測試全通過（`test_pipeline.py`）

---

## M7 — HTTP API

- [x] T7-1 `handle_get_news()` 實作
- [x] T7-2 `handle_get_news_dates()` 實作
- [x] T7-3 `handle_subscribe()` 實作
- [x] T7-4 `handle_unsubscribe()` 實作
- [x] T7-5 HTTP Triggers 在 `function_app.py` 註冊
- [x] T7-6 單元測試全通過（`test_api.py`）

---

## M8 — News List Page

- [x] T8-1 TypeScript 型別定義（`frontend/types/news.ts`）
- [x] T8-2 `lib/api.ts` 建立（`fetchNews`、`fetchAvailableDates`）
- [x] T8-3 `layout.tsx` 佈局建立
- [x] T8-4 首頁 `page.tsx` 實作（loading / empty / content 三種狀態）
- [x] T8-5 `LoadingSkeleton` 元件建立

---

## M9 — History Page

- [x] T9-1 History Page 實作（日期選擇 + 內容顯示）
- [x] T9-2 `/api/news/dates` 整合驗證

---

## M10 — Subscribe Page

- [x] T10-1 Subscribe Page 頁面建立
- [x] T10-2 訂閱端對端流程驗證

---

## M11 — Shared Components

- [x] T11-1 `ArticleCard` 元件（展開/收合 + sentiment badge）
- [x] T11-2 `CategorySection` 元件（空列表不渲染）
- [x] T11-3 `DatePicker` 元件（日期高亮 + 空狀態）
- [x] T11-4 `SubscribeForm` 元件（狀態機 + 前端驗證）

---

## 建議開發順序

```
M0（專案設定）
  └─► M1（RSS Fetcher）
        └─► M2（Deduplicator）
              └─► M3（AI Analyzer）
                    └─► M4（Storage）
                          ├─► M5（Email Notifier）
                          │     └─► M6（Orchestrator）★ 後端核心完成
                          └─► M7（HTTP API）

M0（專案設定）
  └─► M11（Shared Components）
        ├─► M8（News List Page）
        ├─► M9（History Page）
        └─► M10（Subscribe Page）★ 前端核心完成
```

> Backend（M1-M7）與 Frontend（M11, M8-M10）可**並行開發**，以 API 合約（`docs/detailed-design.md` Section 7）為對接介面。
