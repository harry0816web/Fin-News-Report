# M7 — HTTP API

> **層級**：Backend  
> **依賴**：M4（Storage）  
> **相關檔案**：`backend/api/`、`backend/function_app.py`

---

## 任務列表

### T7-1 實作 `GET /api/news` handler

**檔案**：`backend/api/news_handler.py`

```python
from datetime import date as Date, datetime, timezone, timedelta
from storage.abstract_storage import AbstractStorageClient

def handle_get_news(
    date_str: str | None,
    storage: AbstractStorageClient,
) -> dict:
    """
    回傳 (status_code: int, body: dict) tuple。
    date_str 為 None 時，預設今日（台灣時間 UTC+8）。
    """
```

**業務邏輯**：

| 情境 | status | body |
|------|--------|------|
| date_str 為 None | 取今日台灣時間（`datetime.now(tz=timezone(timedelta(hours=8))).date()`） | — |
| 日期格式不合 YYYY-MM-DD | 400 | `{"error": "invalid date format"}` |
| 日期超出今天 7 天前 | 400 | `{"error": "date out of range"}` |
| 找不到該日資料 | 404 | `{"error": "not found"}` |
| 正常 | 200 | `DailyDigest.to_dict()` |

**驗收**：傳入合法 date_str 且 storage 有資料時，回傳 `(200, digest_dict)`

---

### T7-2 實作 `GET /api/news/dates` handler

**檔案**：`backend/api/news_handler.py`（同上）

```python
def handle_get_news_dates(
    storage: AbstractStorageClient,
) -> dict:
    """
    回傳 (200, {"dates": ["2026-05-16", "2026-05-15", ...]})
    """
```

**驗收**：dates 列表按由新至舊排序

---

### T7-3 實作 `POST /api/subscribe` handler

**檔案**：`backend/api/subscribe_handler.py`

```python
from email_validator import validate_email, EmailNotValidError
from storage.abstract_storage import AbstractStorageClient

def handle_subscribe(
    body: dict,
    storage: AbstractStorageClient,
) -> tuple[int, dict]:
    ...
```

**業務邏輯**：

| 情境 | status | body |
|------|--------|------|
| body 無 email 欄位 | 400 | `{"error": "missing email"}` |
| email 格式不合法 | 400 | `{"error": "invalid email"}` |
| email 已存在 | 200 | `{"message": "already subscribed"}` |
| 新增成功 | 201 | `{"message": "subscribed"}` |

**驗收**：`POST {"email": "test@example.com"}` 回傳 `(201, {"message": "subscribed"})`

---

### T7-4 實作 `GET /api/unsubscribe` handler

**檔案**：`backend/api/subscribe_handler.py`（同上）

```python
def handle_unsubscribe(
    email: str,
    storage: AbstractStorageClient,
) -> tuple[int, dict]:
    ...
```

**業務邏輯**：

| 情境 | status | body |
|------|--------|------|
| 移除成功 | 200 | `{"message": "unsubscribed"}` |
| email 不存在 | 200 | `{"message": "not found"}` |

**驗收**：移除不存在的 email 不報錯，回傳 `(200, {"message": "not found"})`

---

### T7-5 在 `function_app.py` 註冊 HTTP Triggers

**檔案**：`backend/function_app.py`（在 T6-3 基礎上新增）

```python
import json

@app.route(route="news", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_news(req: func.HttpRequest) -> func.HttpResponse:
    date_str = req.params.get("date")
    storage  = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    status, body = handle_get_news(date_str, storage)
    return func.HttpResponse(json.dumps(body, ensure_ascii=False), status_code=status,
                             mimetype="application/json")

@app.route(route="news/dates", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_news_dates(req: func.HttpRequest) -> func.HttpResponse:
    storage = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    status, body = handle_get_news_dates(storage)
    return func.HttpResponse(json.dumps(body, ensure_ascii=False), status_code=status,
                             mimetype="application/json")

@app.route(route="subscribe", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def post_subscribe(req: func.HttpRequest) -> func.HttpResponse:
    body    = req.get_json()
    storage = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    status, resp = handle_subscribe(body, storage)
    return func.HttpResponse(json.dumps(resp, ensure_ascii=False), status_code=status,
                             mimetype="application/json")

@app.route(route="unsubscribe", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_unsubscribe(req: func.HttpRequest) -> func.HttpResponse:
    email   = req.params.get("email", "")
    storage = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    status, resp = handle_unsubscribe(email, storage)
    return func.HttpResponse(json.dumps(resp, ensure_ascii=False), status_code=status,
                             mimetype="application/json")
```

**CORS 設定**：在 `host.json` 的 `extensions.http.routePrefix` 設定或透過 Azure Portal 設定 CORS，允許前端 URL。

**驗收**：`uv run func start` 後，`curl http://localhost:7071/api/news` 回傳 JSON

---

### T7-6 撰寫單元測試

**檔案**：`backend/tests/test_api.py`

使用 `InMemoryStorageClient` 直接呼叫 handler function。

| 測試案例 | 情境 |
|---------|------|
| `test_get_news_today_success` | storage 有今日資料，回傳 200 + digest |
| `test_get_news_specific_date` | 指定有資料的日期，回傳 200 |
| `test_get_news_invalid_format` | date="2026/05/16"，回傳 400 |
| `test_get_news_out_of_range` | date 超出 7 天前，回傳 400 |
| `test_get_news_not_found` | 指定無資料的日期，回傳 404 |
| `test_get_news_dates` | 有 3 筆資料，回傳 dates 列表長度為 3 |
| `test_subscribe_success` | 新 email，回傳 201 |
| `test_subscribe_duplicate` | 已存在 email，回傳 200 |
| `test_subscribe_invalid_email` | "notanemail"，回傳 400 |
| `test_subscribe_missing_email` | `{}` body，回傳 400 |
| `test_unsubscribe_success` | 存在的 email，回傳 200 |
| `test_unsubscribe_not_found` | 不存在的 email，回傳 200 |

**執行**：`uv run pytest backend/tests/test_api.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T7-1 `handle_get_news()` 實作完成
- [ ] T7-2 `handle_get_news_dates()` 實作完成
- [ ] T7-3 `handle_subscribe()` 實作完成
- [ ] T7-4 `handle_unsubscribe()` 實作完成
- [ ] T7-5 HTTP Triggers 在 `function_app.py` 註冊完成
- [ ] T7-6 所有單元測試通過
