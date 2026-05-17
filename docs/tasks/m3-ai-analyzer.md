# M3 — AI Analyzer

> **層級**：Backend  
> **依賴**：M1（`RawArticle`）  
> **相關檔案**：`backend/analyzer/`

---

## 任務列表

### T3-1 定義輸出資料模型

**檔案**：`backend/analyzer/models.py`

```python
from dataclasses import dataclass
from enum import Enum

class Category(str, Enum):
    TECH_MARKET    = "科技股市"
    MACRO_ECONOMY  = "總體經濟"
    LISTED_COMPANY = "上市公司公告"
    INTERNATIONAL  = "國際財經"

@dataclass
class AnalyzedArticle:
    id: str                # UUID 字串
    title: str
    url: str
    source: str
    published_at: str      # ISO 8601 帶時區
    category: str          # Category 枚舉值
    summary: str           # AI 繁體中文摘要
    impact_analysis: str   # AI 影響分析
    sentiment: str         # "positive" | "negative" | "neutral"
```

**驗收**：`from analyzer.models import AnalyzedArticle, Category` 可正常 import

---

### T3-2 定義自定義例外

**檔案**：`backend/analyzer/exceptions.py`

```python
class GeminiQuotaError(Exception):
    """HTTP 429：API 配額超出"""

class GeminiAPIError(Exception):
    """HTTP 5xx 或連線失敗（重試後仍失敗）"""

class GeminiResponseParseError(Exception):
    """Gemini 回傳的 JSON 格式無效"""
```

**驗收**：三種例外可分別 raise 與 catch

---

### T3-3 實作 `build_user_prompt()`

**檔案**：`backend/analyzer/prompt_builder.py`

- 將 `list[RawArticle]` 序列化為 JSON 字串（含 title、source、url、published_at、description）
- 組裝完整指令，包含：
  1. 從輸入選出 10-15 則最重要的財經新聞
  2. 每則歸入四類之一
  3. 每則生成 2-3 段繁體中文摘要
  4. 每則生成對台灣股市/科技業的潛在影響分析（含 sentiment）
  5. 以指定 JSON Schema 輸出，**不要包含 markdown 程式碼區塊**

```python
SYSTEM_PROMPT = """
你是一位台灣財經分析師。你的工作是從每日新聞中篩選重要資訊並提供分析。
輸出語言：繁體中文。
"""

# 要求 Gemini 輸出的 JSON Schema（嵌入於 prompt 中）
OUTPUT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "url": {"type": "string"},
            "source": {"type": "string"},
            "published_at": {"type": "string"},
            "category": {"type": "string", "enum": ["科技股市", "總體經濟", "上市公司公告", "國際財經"]},
            "summary": {"type": "string"},
            "impact_analysis": {"type": "string"},
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
        },
        "required": ["title", "url", "source", "published_at", "category", "summary", "impact_analysis", "sentiment"]
    }
}

def build_user_prompt(articles: list[RawArticle]) -> str:
    ...
```

**驗收**：`build_user_prompt(articles)` 回傳非空字串，且包含 articles 的 title 資訊

---

### T3-4 實作 `GeminiAnalyzer` 類別

**檔案**：`backend/analyzer/gemini_analyzer.py`

**規格**：
- 建構子接受 `api_key: str` 與可選的 `client`（依賴注入，用於測試）
- 呼叫 Gemini API：模型 `gemini-2.0-flash`，`response_mime_type="application/json"`，`temperature=0.2`
- 解析回傳 JSON，為每篇文章生成 UUID id，組裝 `AnalyzedArticle` 列表
- HTTP 429 → 拋出 `GeminiQuotaError`
- HTTP 5xx / 連線失敗 → 重試最多 3 次（間隔 5 秒），仍失敗拋出 `GeminiAPIError`
- JSON 解析失敗 → 拋出 `GeminiResponseParseError`

```python
import uuid
import time
import json
import logging

class GeminiAnalyzer:
    def __init__(self, api_key: str, client=None):
        ...

    def analyze(self, articles: list[RawArticle]) -> list[AnalyzedArticle]:
        ...
```

**驗收**：
- 傳入 mock client 回傳合法 JSON 時，正確回傳 `list[AnalyzedArticle]`
- 每個 AnalyzedArticle 的 `id` 為合法 UUID 格式

---

### T3-5 撰寫單元測試

**檔案**：`backend/tests/test_analyzer.py`

使用 `unittest.mock.MagicMock` 模擬 Gemini client。

| 測試案例 | 情境 |
|---------|------|
| `test_analyze_success` | mock client 回傳 10 篇合法 JSON，驗證 AnalyzedArticle 欄位正確，id 為 UUID |
| `test_analyze_quota_exceeded` | mock client 回傳 HTTP 429，驗證拋出 `GeminiQuotaError` |
| `test_analyze_api_error_with_retry` | mock client 連續拋出 HTTP 500，驗證重試 3 次後拋出 `GeminiAPIError` |
| `test_analyze_invalid_json` | mock client 回傳非 JSON 字串，驗證拋出 `GeminiResponseParseError` |
| `test_analyze_missing_field` | mock client 回傳缺少必要欄位的 JSON，驗證拋出 `GeminiResponseParseError` |

**執行**：`uv run pytest backend/tests/test_analyzer.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T3-1 `AnalyzedArticle` 與 `Category` 定義完成
- [ ] T3-2 三種例外定義完成
- [ ] T3-3 `build_user_prompt()` 實作完成
- [ ] T3-4 `GeminiAnalyzer.analyze()` 實作完成（含重試邏輯）
- [ ] T3-5 所有單元測試通過
