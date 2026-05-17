# M10 — Subscribe Page

> **層級**：Frontend  
> **依賴**：M11（`SubscribeForm` 元件）  
> **相關檔案**：`frontend/app/subscribe/page.tsx`

---

## 任務列表

### T10-1 實作 Subscribe Page

**檔案**：`frontend/app/subscribe/page.tsx`

**要點**：
- 靜態內容，使用 Server Component（不需 `'use client'`）
- 引入 `<SubscribeForm>` client component 處理互動

```tsx
// app/subscribe/page.tsx
import SubscribeForm from "@/components/SubscribeForm";

export default function SubscribePage() {
  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-2">訂閱台灣財經日報</h1>
      <p className="text-gray-500 mb-8">每天早上 09:00 收到最新財經摘要</p>
      <SubscribeForm />
    </main>
  );
}
```

**驗收**：頁面正常渲染，`/subscribe` 路徑可訪問

---

### T10-2 驗證訂閱表單端對端流程

- 輸入合法 email → 點擊訂閱 → 確認成功訊息顯示
- 輸入重複 email → 確認「已訂閱」訊息
- 輸入不合法 email → 確認錯誤提示（前端驗證先攔截）

**驗收**：手動測試三種情境均有正確反饋

---

## 完成條件

- [ ] T10-1 Subscribe Page 頁面建立完成
- [ ] T10-2 訂閱端對端流程驗證完成
