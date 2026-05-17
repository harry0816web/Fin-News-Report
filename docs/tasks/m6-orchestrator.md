# M6 — Orchestrator

> **層級**：Backend  
> **依賴**：M1、M2、M3、M4、M5 全部完成  
> **相關檔案**：`backend/orchestrator/`、`backend/function_app.py`

---

## 任務列表

### T6-1 定義 `PipelineResult` dataclass

**檔案**：`backend/orchestrator/models.py`

```python
from dataclasses import dataclass, field
from typing import Literal

PipelineStatus = Literal["success", "failed", "quota_exceeded"]

@dataclass
class PipelineResult:
    status: PipelineStatus
    article_count: int = 0
    error_message: str = ""
```

**驗收**：可正常初始化，status 為三種之一

---

### T6-2 實作 `run_daily_pipeline()`

**檔案**：`backend/orchestrator/pipeline.py`

```python
import logging
from datetime import datetime, timezone
from fetcher.rss_fetcher import fetch_all_sources
from deduplicator.deduplicator import deduplicate
from analyzer.gemini_analyzer import GeminiAnalyzer
from analyzer.exceptions import GeminiQuotaError, GeminiAPIError
from storage.abstract_storage import AbstractStorageClient
from storage.models import DailyDigest
from notifier.email_notifier import EmailNotifier
from orchestrator.models import PipelineResult

def run_daily_pipeline(
    storage: AbstractStorageClient,
    notifier: EmailNotifier,
    analyzer: GeminiAnalyzer,
) -> PipelineResult:
    ...
```

**執行流程（按序實作）**：

```
Step 1: raw_articles = fetch_all_sources()
        └── 若 raw_articles 為空 → log ERROR → return PipelineResult(status="failed")

Step 2: deduped = deduplicate(raw_articles)
        → log INFO：f"Deduplicated: {len(raw_articles)} → {len(deduped)}"

Step 3: try:
            analyzed = analyzer.analyze(deduped)
        except GeminiQuotaError:
            → subscribers = storage.get_subscribers()
            → notifier.send_quota_exceeded_notice([s.email for s in subscribers])
            → return PipelineResult(status="quota_exceeded")
        except GeminiAPIError as e:
            → log ERROR
            → return PipelineResult(status="failed", error_message=str(e))

Step 4: digest = DailyDigest(
            date=today_tw_str,
            generated_at=now_iso,
            article_count=len(analyzed),
            articles=analyzed,
        )
        storage.save_daily_digest(digest)

Step 5: storage.cleanup_old_digests(keep_days=7)

Step 6: subscribers = storage.get_subscribers()
        若 subscribers 為空 → log INFO "No subscribers, skipping email"
        否則 → notifier.send_daily_digest(digest, [s.email for s in subscribers])

Step 7: return PipelineResult(status="success", article_count=len(analyzed))
```

**驗收**：以 `InMemoryStorageClient` 與 mock analyzer/notifier 可完整執行流程

---

### T6-3 在 `function_app.py` 註冊 Timer Trigger

**檔案**：`backend/function_app.py`

```python
import logging
import os
import azure.functions as func
from orchestrator.pipeline import run_daily_pipeline
from storage.blob_storage import BlobStorageClient
from notifier.email_notifier import EmailNotifier
from analyzer.gemini_analyzer import GeminiAnalyzer

app = func.FunctionApp()

@app.timer_trigger(
    schedule="0 0 1 * * *",    # 每天 01:00 UTC = 09:00 台灣時間
    arg_name="timer",
    run_on_startup=False,
)
def daily_pipeline_trigger(timer: func.TimerRequest) -> None:
    storage  = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    notifier = EmailNotifier(
        acs_connection_string=os.environ["ACS_CONNECTION_STRING"],
        sender_address=os.environ["ACS_SENDER_ADDRESS"],
    )
    analyzer = GeminiAnalyzer(api_key=os.environ["GEMINI_API_KEY"])

    result = run_daily_pipeline(storage, notifier, analyzer)
    logging.info(f"Pipeline completed: {result}")
```

**驗收**：`function_app.py` 可正常 import，無語法錯誤

---

### T6-4 撰寫整合測試

**檔案**：`backend/tests/test_pipeline.py`

使用 `InMemoryStorageClient` + `MagicMock` 模擬 analyzer 與 notifier。

| 測試案例 | 情境 |
|---------|------|
| `test_pipeline_success` | 正常流程：驗證 digest 已存入 storage，email 已發送，回傳 `status="success"` |
| `test_pipeline_no_articles` | fetch 回傳空列表，驗證回傳 `status="failed"`，不呼叫 analyzer |
| `test_pipeline_quota_exceeded` | analyzer 拋出 `GeminiQuotaError`，驗證發送 quota 通知信，回傳 `status="quota_exceeded"` |
| `test_pipeline_api_error` | analyzer 拋出 `GeminiAPIError`，驗證回傳 `status="failed"`，不存入 storage |
| `test_pipeline_no_subscribers` | 正常流程但 storage 無訂閱者，驗證 `send_daily_digest` 未被呼叫 |
| `test_pipeline_cleanup_called` | 驗證 `cleanup_old_digests` 在 save 之後被呼叫 |

**執行**：`uv run pytest backend/tests/test_pipeline.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T6-1 `PipelineResult` 定義完成
- [ ] T6-2 `run_daily_pipeline()` 實作完成
- [ ] T6-3 Timer Trigger 在 `function_app.py` 註冊完成
- [ ] T6-4 所有整合測試通過
