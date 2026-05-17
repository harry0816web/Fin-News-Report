# M4 — Storage

> **層級**：Backend  
> **依賴**：M3（`AnalyzedArticle`、`DailyDigest`）  
> **相關檔案**：`backend/storage/`

---

## 任務列表

### T4-1 定義 `DailyDigest` 與 `Subscriber` 資料模型

**檔案**：`backend/storage/models.py`

```python
from dataclasses import dataclass, field
from datetime import date as Date
from analyzer.models import AnalyzedArticle

@dataclass
class DailyDigest:
    date: str                          # "YYYY-MM-DD"
    generated_at: str                  # ISO 8601 帶時區
    article_count: int
    articles: list[AnalyzedArticle]

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "DailyDigest": ...

@dataclass
class Subscriber:
    email: str
    subscribed_at: str                 # ISO 8601 帶時區
```

**驗收**：`DailyDigest.to_dict()` 可序列化為合法 JSON，`DailyDigest.from_dict()` 可還原

---

### T4-2 定義 `AbstractStorageClient` 抽象類別

**檔案**：`backend/storage/abstract_storage.py`

```python
from abc import ABC, abstractmethod
from datetime import date as Date
from storage.models import DailyDigest, Subscriber

class AbstractStorageClient(ABC):
    @abstractmethod
    def save_daily_digest(self, digest: DailyDigest) -> None: ...

    @abstractmethod
    def get_daily_digest(self, date: Date) -> DailyDigest | None: ...

    @abstractmethod
    def list_available_dates(self) -> list[Date]: ...

    @abstractmethod
    def cleanup_old_digests(self, keep_days: int = 7) -> int: ...

    @abstractmethod
    def get_subscribers(self) -> list[Subscriber]: ...

    @abstractmethod
    def add_subscriber(self, email: str) -> bool: ...

    @abstractmethod
    def remove_subscriber(self, email: str) -> bool: ...
```

**驗收**：可繼承此類別並實作所有抽象方法

---

### T4-3 實作 `InMemoryStorageClient`（測試用）

**檔案**：`backend/storage/in_memory_storage.py`

- 繼承 `AbstractStorageClient`
- 使用 `dict` 儲存 digests（key = date 字串）
- 使用 `list` 儲存 subscribers
- 實作所有 7 個方法，行為與 BlobStorageClient 一致

**驗收**：`InMemoryStorageClient` 可通過 T4-5 的所有單元測試

---

### T4-4 實作 `BlobStorageClient`

**檔案**：`backend/storage/blob_storage.py`

使用 `azure-storage-blob` SDK：

```python
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceNotFoundError

class BlobStorageClient(AbstractStorageClient):

    def __init__(self, connection_string: str, container_name: str = "fin-news"):
        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = container_name
```

**各方法實作要點**：

| 方法 | Blob 路徑 | 要點 |
|------|-----------|------|
| `save_daily_digest` | `news/YYYY-MM-DD.json` | `upload_blob(..., overwrite=True)` |
| `get_daily_digest` | `news/YYYY-MM-DD.json` | 不存在時 catch `ResourceNotFoundError`，回傳 `None` |
| `list_available_dates` | `news/` 前綴 list | 解析 blob 名稱，由新至舊排序，最多 7 筆 |
| `cleanup_old_digests` | `news/` 前綴 list | 刪除超過 keep_days 天的 blob，回傳刪除數 |
| `get_subscribers` | `subscribers/list.json` | 不存在時回傳 `[]` |
| `add_subscriber` | `subscribers/list.json` | ETag 條件式寫入，重試最多 3 次 |
| `remove_subscriber` | `subscribers/list.json` | ETag 條件式寫入，重試最多 3 次 |

**驗收**：以真實 Azure Blob Storage（或 Azurite 本地模擬）可完成 save/get 往返操作

---

### T4-5 撰寫單元測試

**檔案**：`backend/tests/test_storage.py`

使用 `InMemoryStorageClient` 進行所有測試（不需真實 Azure）。

| 測試案例 | 情境 |
|---------|------|
| `test_save_and_get_daily_digest` | 儲存後可正確讀取，欄位相符 |
| `test_get_nonexistent_digest` | 查詢不存在日期回傳 `None` |
| `test_list_available_dates_sorted` | 多筆資料，確認由新至舊排序 |
| `test_list_available_dates_max_7` | 超過 7 筆時，只回傳最新 7 筆 |
| `test_cleanup_old_digests` | 超過 7 天的資料被刪除，回傳正確刪除數 |
| `test_add_subscriber_success` | 新增成功回傳 `True` |
| `test_add_subscriber_duplicate` | 重複 email 回傳 `False` |
| `test_remove_subscriber_success` | 移除成功回傳 `True` |
| `test_remove_subscriber_not_found` | 不存在的 email 回傳 `False` |

**執行**：`uv run pytest backend/tests/test_storage.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T4-1 `DailyDigest` 與 `Subscriber` 定義完成（含序列化方法）
- [ ] T4-2 `AbstractStorageClient` 定義完成
- [ ] T4-3 `InMemoryStorageClient` 實作完成
- [ ] T4-4 `BlobStorageClient` 實作完成
- [ ] T4-5 所有單元測試通過
