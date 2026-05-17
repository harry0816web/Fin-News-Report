# M11 — Shared Components

> **層級**：Frontend  
> **依賴**：M8（TypeScript 型別定義）  
> **相關檔案**：`frontend/components/`

---

## 任務列表

### T11-1 實作 `ArticleCard` 元件

**檔案**：`frontend/components/ArticleCard.tsx`

```typescript
interface ArticleCardProps {
  article: AnalyzedArticle;
}
```

**收合狀態（預設）**：
- 文章標題（粗體）
- 來源名稱 + 發布時間（次要文字）
- Sentiment badge（顏色：positive=綠、negative=紅、neutral=灰）
- 展開按鈕（`▶` 或 `▼`）

**展開狀態**：
- 額外顯示：
  - `📋 新聞摘要` 段落
  - `📈 對台灣市場的潛在影響` 段落（影響分析支援換行，`whitespace-pre-line`）
  - `🔗 原文連結`（新分頁開啟）
- 收合按鈕

**狀態管理**：
```typescript
const [isExpanded, setIsExpanded] = useState(false);
```

**驗收**：
- 點擊標題/按鈕可展開與收合
- Sentiment badge 顯示正確顏色
- 展開時內容完整

---

### T11-2 實作 `CategorySection` 元件

**檔案**：`frontend/components/CategorySection.tsx`

```typescript
interface CategorySectionProps {
  category: string;
  articles: AnalyzedArticle[];
}
```

**UI**：
```tsx
<section>
  <h2 className="...">【{category}】</h2>
  <div className="space-y-3">
    {articles.map(article => (
      <ArticleCard key={article.id} article={article} />
    ))}
  </div>
</section>
```

- 若 `articles.length === 0`，不渲染此 section（`return null`）

**驗收**：傳入有文章的 category，正確渲染多個 ArticleCard；空 articles 時不渲染

---

### T11-3 實作 `DatePicker` 元件

**檔案**：`frontend/components/DatePicker.tsx`

```typescript
interface DatePickerProps {
  availableDates: string[];    // ["2026-05-16", "2026-05-15", ...]
  selectedDate: string;
  onChange: (date: string) => void;
}
```

**UI**：
- 以按鈕列表呈現可選日期（每個日期一個按鈕）
- 選中日期：高亮樣式（藍色背景）
- 未選中：灰色背景
- 顯示格式：`05/16`（MM/DD）或 `5月16日`
- `availableDates` 為空時：顯示「暫無歷史資料」

**驗收**：
- 點擊日期按鈕觸發 `onChange`
- selectedDate 對應按鈕有高亮

---

### T11-4 實作 `SubscribeForm` 元件

**檔案**：`frontend/components/SubscribeForm.tsx`

```typescript
type FormStatus = "idle" | "loading" | "success" | "error" | "already_subscribed";
```

**狀態機**：
```
idle → loading（點擊訂閱）
loading → success（API 201）
loading → already_subscribed（API 200）
loading → error（API 400 / 網路錯誤）
success / error / already_subscribed → idle（重置按鈕）
```

**前端驗證**（在送出前）：
- Email 欄位非空
- 符合基本 email 格式（`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`）
- 驗證失敗時顯示錯誤文字，不呼叫 API

**各狀態 UI**：

| 狀態 | 顯示 |
|------|------|
| idle | input + 訂閱按鈕 |
| loading | 按鈕 disabled + spinner |
| success | ✅ 訂閱成功！將於明天起收到每日財經摘要 |
| already_subscribed | ℹ️ 此 Email 已訂閱 |
| error | ❌ 訂閱失敗，請稍後再試 |

**驗收**：
- 空 email 送出時顯示前端錯誤
- 載入中按鈕 disabled
- API 回傳各種狀態時顯示對應訊息

---

## 完成條件

- [ ] T11-1 `ArticleCard` 實作完成（展開/收合、sentiment badge）
- [ ] T11-2 `CategorySection` 實作完成（空 articles 不渲染）
- [ ] T11-3 `DatePicker` 實作完成（日期高亮、空狀態）
- [ ] T11-4 `SubscribeForm` 實作完成（狀態機、前端驗證）
