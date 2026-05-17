# M9 — History Page

> **層級**：Frontend  
> **依賴**：M8（api.ts 已建立）、M11（Shared Components）  
> **相關檔案**：`frontend/app/history/page.tsx`

---

## 任務列表

### T9-1 實作 History Page

**檔案**：`frontend/app/history/page.tsx`

**要點**：
- `'use client'`
- 頁面 mount 時呼叫 `fetchAvailableDates()`，取得可用日期列表
- 預設選中最新一天（列表第一項）
- 選擇日期後呼叫 `fetchNews(selectedDate)` 載入對應資料
- 渲染 `<DatePicker>` + `<CategorySection>` + `<ArticleCard>`（同首頁）

**狀態**：

```typescript
const [availableDates, setAvailableDates] = useState<string[]>([]);
const [selectedDate, setSelectedDate] = useState<string>("");
const [digest, setDigest] = useState<DailyDigest | null>(null);
const [loading, setLoading] = useState(false);
```

**UI 結構**：

```tsx
<main>
  <h1>歷史新聞</h1>
  <DatePicker
    availableDates={availableDates}
    selectedDate={selectedDate}
    onChange={(date) => setSelectedDate(date)}
  />
  {loading && <LoadingSkeleton />}
  {digest && CATEGORY_ORDER.map(category => (
    <CategorySection ... />
  ))}
  {!loading && !digest && <EmptyState message="此日期無資料" />}
</main>
```

**驗收**：切換日期時，內容正確更新，loading 狀態正確顯示

---

### T9-2 驗證 `GET /api/news/dates` 端點整合

- 確認 `fetchAvailableDates()` 正確呼叫 `/api/news/dates`
- 確認回傳的日期格式為 `YYYY-MM-DD`
- 若 API 回傳空陣列，DatePicker 顯示「暫無歷史資料」

**驗收**：手動測試（或 E2E）可正確列出過去有資料的日期

---

## 完成條件

- [ ] T9-1 History Page 實作完成（日期選擇 + 內容顯示）
- [ ] T9-2 `/api/news/dates` 端點整合驗證完成
