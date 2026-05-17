# M0 — Project Setup

> 前置任務，其他所有 module 依賴此項完成

---

## 任務列表

### T0-1 初始化 Python 後端專案結構

**目標**：建立 `backend/` 目錄骨架與 `pyproject.toml`

**步驟**：
```
fin-news/
├── backend/
│   ├── function_app.py        ← 空白進入點
│   ├── fetcher/__init__.py
│   ├── deduplicator/__init__.py
│   ├── analyzer/__init__.py
│   ├── storage/__init__.py
│   ├── notifier/__init__.py
│   │   └── templates/         ← 建立空目錄
│   ├── orchestrator/__init__.py
│   ├── api/__init__.py
│   └── tests/__init__.py
├── pyproject.toml
└── host.json
```

**驗收**：`uv run python -c "import backend"` 不報錯

---

### T0-2 安裝 Python 依賴套件

**目標**：在 `pyproject.toml` 加入所有 backend 依賴

```toml
[project]
name = "fin-news-backend"
requires-python = ">=3.11"
dependencies = [
    "azure-functions",
    "azure-storage-blob",
    "azure-communication-email",
    "feedparser",
    "httpx",
    "google-generativeai",
    "jinja2",
    "email-validator",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
]
```

**執行**：`uv sync`

**驗收**：`uv run pytest --version` 成功執行

---

### T0-3 建立 `host.json`（Azure Functions 設定）

**目標**：`backend/host.json` 包含基本 Functions v4 設定

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

**驗收**：檔案存在且 JSON 格式正確

---

### T0-4 初始化 Next.js 前端專案

**目標**：在 `frontend/` 建立 Next.js App Router 專案（靜態匯出模式）

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

在 `next.config.ts` 加入靜態匯出：
```typescript
const nextConfig = {
  output: 'export',
};
export default nextConfig;
```

**驗收**：`cd frontend && npm run build` 成功產出 `out/` 目錄

---

### T0-5 建立 `.env.example` 與本地 `.env`

**目標**：確保環境變數範本與本地設定檔存在

```bash
# .env.example
GEMINI_API_KEY=
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER_NAME=fin-news
ACS_CONNECTION_STRING=
ACS_SENDER_ADDRESS=
NEXT_PUBLIC_API_BASE_URL=http://localhost:7071
```

**驗收**：`.env.example` 已提交至 git，`.env` 已列入 `.gitignore`

---

### T0-6 建立 `backend/function_app.py` 骨架

**目標**：建立最小可執行的 Azure Functions 進入點

```python
# backend/function_app.py
import logging
import azure.functions as func

app = func.FunctionApp()

# Timer Trigger 與 HTTP Trigger 將在後續 module 中註冊
```

**驗收**：`uv run func start`（若已安裝 Azure Functions Core Tools）可啟動，或直接 import 不報錯

---

## 完成條件

- [ ] T0-1 目錄結構建立完成
- [ ] T0-2 Python 依賴安裝完成
- [ ] T0-3 host.json 建立完成
- [ ] T0-4 Next.js 專案初始化完成
- [ ] T0-5 環境變數範本建立完成
- [ ] T0-6 function_app.py 骨架建立完成
