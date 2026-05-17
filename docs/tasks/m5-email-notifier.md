# M5 — Email Notifier

> **層級**：Backend  
> **依賴**：M4（`DailyDigest`）  
> **相關檔案**：`backend/notifier/`

---

## 任務列表

### T5-1 建立每日摘要 HTML 模板

**檔案**：`backend/notifier/templates/daily_digest.html`

使用 **Jinja2** 模板語法，結構：

```
Header：📊 台灣財經日報 {{ date }}
---
{% for category, articles in grouped_articles.items() %}
  【{{ category }}】
  {% for article in articles %}
    [{{ article.sentiment_badge }}] {{ article.title }}
    {{ article.source }} | {{ article.published_at }}
    
    📋 摘要
    {{ article.summary }}
    
    📈 影響分析
    {{ article.impact_analysis }}
    
    🔗 原文連結：{{ article.url }}
  {% endfor %}
{% endfor %}
---
Footer：如要退訂，請點擊 {{ unsubscribe_url }}
```

**驗收**：Jinja2 `Template.render()` 可正確渲染，不拋出 `TemplateError`

---

### T5-2 建立 Quota 超出通知模板

**檔案**：`backend/notifier/templates/quota_exceeded.html`

內容：今日因 Gemini API 配額超出，無法生成財經摘要。請直接查閱各財經媒體。附上來源連結列表。

**驗收**：可正常渲染

---

### T5-3 定義 `SendResult` dataclass

**檔案**：`backend/notifier/models.py`

```python
from dataclasses import dataclass

@dataclass
class SendResult:
    success_count: int
    failure_count: int
    errors: list[str] = field(default_factory=list)
```

**驗收**：可正常初始化與存取欄位

---

### T5-4 實作 `EmailNotifier` 類別

**檔案**：`backend/notifier/email_notifier.py`

```python
from jinja2 import Environment, FileSystemLoader
from azure.communication.email import EmailClient

class EmailNotifier:

    def __init__(
        self,
        acs_connection_string: str,
        sender_address: str,
        acs_client=None,     # 依賴注入，測試時傳入 mock
    ):
        ...
```

**`send_daily_digest()` 實作要點**：
1. 使用 Jinja2 渲染 `daily_digest.html`，傳入 `digest` 與 `unsubscribe_url`
2. 將 articles 依 category 分組（`groupby`）
3. `recipients` 超過 50 人時，分批（每批 ≤ 50）發送
4. 每批呼叫 ACS `send()` 方法
5. 收集成功/失敗數，回傳 `SendResult`

**`send_quota_exceeded_notice()` 實作要點**：
1. 渲染 `quota_exceeded.html`
2. 寄送給 `recipients`
3. 回傳 `SendResult`

**驗收**：使用 mock ACS client 可完成發送流程，無例外拋出

---

### T5-5 撰寫單元測試

**檔案**：`backend/tests/test_notifier.py`

使用 `unittest.mock.MagicMock` 模擬 ACS client。

| 測試案例 | 情境 |
|---------|------|
| `test_send_daily_digest_html_contains_articles` | 渲染後的 HTML 包含所有文章標題 |
| `test_send_daily_digest_unsubscribe_link` | HTML 包含正確的退訂連結（含 email encoding） |
| `test_send_daily_digest_batch_over_50` | 60 個訂閱者，驗證 ACS client.send() 被呼叫 2 次 |
| `test_send_daily_digest_returns_send_result` | 回傳 `SendResult`，success_count 正確 |
| `test_send_quota_exceeded_notice` | 驗證 ACS client.send() 被呼叫，主旨包含「配額」相關文字 |

**執行**：`uv run pytest backend/tests/test_notifier.py -v`

**驗收**：所有測試通過

---

## 完成條件

- [ ] T5-1 `daily_digest.html` 模板建立完成
- [ ] T5-2 `quota_exceeded.html` 模板建立完成
- [ ] T5-3 `SendResult` 定義完成
- [ ] T5-4 `EmailNotifier` 實作完成（含分批發送）
- [ ] T5-5 所有單元測試通過
