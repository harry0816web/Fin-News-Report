# M2 — Deduplicator

> **層級**：Backend  
> **依賴**：M1（需要 `RawArticle` dataclass）  
> **相關檔案**：`backend/deduplicator/`

---

## 任務列表

### T2-1 實作 `_similarity()` 輔助函式

**檔案**：`backend/deduplicator/deduplicator.py`

- 使用 Python 標準函式庫 `difflib.SequenceMatcher`
- 回傳 `[0.0, 1.0]` 範圍的浮點數

```python
from difflib import SequenceMatcher

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()
```

**驗收**：
- `_similarity("台積電", "台積電")` → `1.0`
- `_similarity("台積電上漲", "台積電下跌")` → 約 `0.7`
- `_similarity("台積電", "鴻海財報")` → < `0.3`

---

### T2-2 實作 `deduplicate()`

**檔案**：`backend/deduplicator/deduplicator.py`（同上）

**演算法**：
1. 以 `published_at` 由新至舊排序輸入列表
2. 建立 `accepted: list[RawArticle] = []`
3. 對每篇文章，計算其標題與 `accepted` 中所有文章標題的相似度
4. 若最大相似度 `>= threshold`，略過此篇（已有近似文章）
5. 否則加入 `accepted`
6. 回傳 `accepted`（已由新至舊排序）

```python
from fetcher.models import RawArticle

def deduplicate(
    articles: list[RawArticle],
    threshold: float = 0.8,
) -> list[RawArticle]:
    ...
```

**驗收**：
- 輸入兩篇標題完全相同的文章，回傳 1 篇
- 輸入相似度 0.85 的文章，回傳 1 篇（保留較新的）
- 輸入相似度 0.5 的文章，兩篇都保留
- 輸入空列表，回傳空列表

---

### T2-3 撰寫單元測試

**檔案**：`backend/tests/test_deduplicator.py`

| 測試案例 | 情境 |
|---------|------|
| `test_identical_titles` | 兩篇標題完全相同，回傳 1 篇 |
| `test_similar_titles_above_threshold` | 相似度 ≥ 0.8，回傳 1 篇（保留 published_at 較新者） |
| `test_similar_titles_below_threshold` | 相似度 < 0.8，兩篇都保留 |
| `test_empty_list` | 輸入 `[]`，回傳 `[]` |
| `test_single_article` | 輸入 1 篇，回傳 1 篇 |
| `test_output_sorted_by_date` | 確認輸出按 published_at 由新至舊排序 |
| `test_custom_threshold` | 傳入 `threshold=0.5`，相似度 0.6 的文章被去重 |

**執行**：`uv run pytest backend/tests/test_deduplicator.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T2-1 `_similarity()` 實作完成
- [ ] T2-2 `deduplicate()` 實作完成
- [ ] T2-3 所有單元測試通過
