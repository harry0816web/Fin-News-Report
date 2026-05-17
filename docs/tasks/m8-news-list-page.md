# M8 — News List Page（首頁）

> **層級**：Frontend  
> **依賴**：M0（Next.js 初始化）、M11（Shared Components）  
> **相關檔案**：`frontend/app/page.tsx`、`frontend/lib/api.ts`、`frontend/types/news.ts`

---

## 任務列表

### T8-1 定義 TypeScript 型別

**檔案**：`frontend/types/news.ts`

```typescript
export type Sentiment = "positive" | "negative" | "neutral";

export type Category =
  | "科技股市"
  | "總體經濟"
  | "上市公司公告"
  | "國際財經";

export interface AnalyzedArticle {
  id: string;
  title: string;
  url: string;
  source: string;
  published_at: string;   // ISO 8601
  category: Category;
  summary: string;
  impact_analysis: string;
  sentiment: Sentiment;
}

export interface DailyDigest {
  date: string;            // "YYYY-MM-DD"
  generated_at: string;
  article_count: number;
  articles: AnalyzedArticle[];
}
```

**驗收**：TypeScript 編譯無型別錯誤

---

### T8-2 建立 `lib/api.ts`

**檔案**：`frontend/lib/api.ts`

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function fetchNews(date?: string): Promise<DailyDigest | null> {
  const url = date
    ? `${API_BASE}/api/news?date=${date}`
    : `${API_BASE}/api/news`;

  const res = await fetch(url);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchAvailableDates(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/news/dates`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.dates ?? [];
}
```

**驗收**：TypeScript 編譯無型別錯誤

---

### T8-3 建立頁面基礎佈局

**檔案**：`frontend/app/layout.tsx`

- 設定 `<html lang="zh-Hant">`
- 引入 Tailwind CSS（Next.js 預設已包含）
- Header 組件：顯示 `台灣財經日報` 標題 + 導覽連結（首頁、歷史、訂閱）
- 設定 `metadata.title = "台灣財經日報"`

**驗收**：`npm run dev` 可正常渲染 layout

---

### T8-4 實作首頁 `page.tsx`

**檔案**：`frontend/app/page.tsx`

**要點**：
- `'use client'` — 使用 client component
- 頁面 mount 時呼叫 `fetchNews()`（使用 `useEffect` + `useState`）
- 載入中：顯示 loading skeleton（3 個佔位卡片）
- 載入成功：依 category 分組，渲染 `<CategorySection>` + `<ArticleCard>`
- 載入空（404）：顯示提示文字「今日摘要尚未生成，請稍後再試」
- 載入失敗：顯示錯誤訊息

**UI 結構**：

```tsx
<main>
  <div className="...">
    <h1>台灣財經日報</h1>
    <span>{today}</span>
    <Link href="/subscribe">訂閱 Email</Link>
  </div>

  {loading && <LoadingSkeleton />}
  {!loading && !digest && <EmptyState />}
  {digest && CATEGORY_ORDER.map(category => (
    <CategorySection
      key={category}
      category={category}
      articles={groupedArticles[category] ?? []}
    />
  ))}
</main>
```

**驗收**：`npm run dev` 可正常顯示頁面，ArticleCard 可展開/收合

---

### T8-5 建立 loading skeleton 元件

**檔案**：`frontend/components/LoadingSkeleton.tsx`

- 3 個動畫佔位卡片（使用 Tailwind `animate-pulse`）
- 每個佔位卡片模擬 ArticleCard 的寬高比例

**驗收**：視覺上有 loading 動畫

---

## 完成條件

- [ ] T8-1 TypeScript 型別定義完成
- [ ] T8-2 `lib/api.ts` 建立完成
- [ ] T8-3 `layout.tsx` 佈局建立完成
- [ ] T8-4 首頁 `page.tsx` 實作完成（loading/empty/content 三種狀態）
- [ ] T8-5 LoadingSkeleton 元件建立完成
