# 部署指南

> 版本：v1.0  
> 日期：2026-05-17  
> 適用環境：Azure for Students + Vercel

---

## 目錄

1. [前置條件](#1-前置條件)
2. [Azure 資源建立（一次性）](#2-azure-資源建立一次性)
3. [環境變數設定](#3-環境變數設定)
4. [Backend 部署（Azure Functions）](#4-backend-部署azure-functions)
5. [Frontend 部署（Vercel）](#5-frontend-部署vercel)
6. [驗證部署結果](#6-驗證部署結果)
7. [日後更新部署](#7-日後更新部署)

---

## 1. 前置條件

### 1.1 本機工具

| 工具 | 安裝指令 | 用途 |
|------|---------|------|
| Azure Functions Core Tools v4 | `brew tap azure/functions && brew install azure-functions-core-tools@4` | 部署 backend 到 Azure Functions |
| Azure CLI | `brew install azure-cli` | 登入 Azure 帳號 |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python 套件管理 |
| Node.js 18+ | `brew install node` | Next.js 前端建置 |

> **注意**：若 Homebrew 報權限錯誤，先執行：
> ```bash
> sudo chown -R $(whoami) /opt/homebrew/Cellar /opt/homebrew/Library
> ```

### 1.2 帳號

- Azure for Students 帳號（已啟用）
- Google AI Studio 帳號（取得 Gemini API Key）
- GitHub 帳號（連接 Vercel）
- Vercel 帳號（免費方案）

---

## 2. Azure 資源建立（一次性）

> 以下步驟只需在第一次部署時執行，日後更新程式碼不需重複。

### Step 1：建立 Resource Group

1. 登入 [portal.azure.com](https://portal.azure.com)
2. 搜尋 **Resource Groups** → **Create**

| 欄位 | 值 |
|------|-----|
| Name | `fin-news-rg` |
| Region | `East Asia` |

### Step 2：建立 Azure Blob Storage

1. 搜尋 **Storage accounts** → **Create**

| 欄位 | 值 |
|------|-----|
| Resource group | `fin-news-rg` |
| Storage account name | `finnewsstorage`（全域唯一） |
| Region | `East Asia` |
| Redundancy | LRS |

2. 建立完成後：**Containers** → **+ Container**
   - Name：`fin-news`
   - Access level：**Private**

3. 取得連線字串：**Security + networking** → **Access keys** → 複製 **Connection string**

### Step 3：建立 Azure Communication Services

1. 搜尋 **Communication Services** → **Create**

| 欄位 | 值 |
|------|-----|
| Resource group | `fin-news-rg` |
| Name | `fin-news-acs` |
| Region | `United States`（ACS Email 限制） |

2. 取得連線字串：**Settings** → **Keys** → 複製 **Primary Connection string**

3. 設定 Email Domain：**Email** → **Domains** → **Add domain** → **Azure managed domain**
   - 建立後複製完整的寄件地址，格式為：`DoNotReply@xxxxxxxx.azurecomm.net`

### Step 4：建立 Azure Functions

1. 搜尋 **Function App** → **Create**
2. Hosting plan 選 **Consumption (Windows)**，進入後將 OS 切換為 **Linux**（Python 需要）

| 欄位 | 值 |
|------|-----|
| Resource group | `fin-news-rg` |
| Function App name | `fin-news-functions` |
| Runtime stack | Python |
| Version | 3.11 |
| Region | `Japan East`（或其他 Azure for Students 允許的區域） |

3. 建立完成後設定環境變數：**Settings** → **Configuration** → **Environment variables** → **+ Add**

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | 從 Google AI Studio 取得 |
| `AZURE_STORAGE_CONNECTION_STRING` | Step 2 取得的連線字串 |
| `AZURE_STORAGE_CONTAINER_NAME` | `fin-news` |
| `ACS_CONNECTION_STRING` | Step 3 取得的連線字串 |
| `ACS_SENDER_ADDRESS` | Step 3 取得的寄件地址 |

4. 設定 CORS：**API** → **CORS** → 新增 Vercel 網址（Step 5 完成後填入）

---

## 3. 環境變數設定

### 本地開發（`.env`）

在專案根目錄建立 `.env`（參考 `.env.example`）：

```bash
GEMINI_API_KEY=你的Gemini_API_Key
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=fin-news
ACS_CONNECTION_STRING=endpoint=https://...;accesskey=...
ACS_SENDER_ADDRESS=DoNotReply@xxxxxxxx.azurecomm.net
NEXT_PUBLIC_API_BASE_URL=https://fin-news-functions-xxxx.japaneast-01.azurewebsites.net
```

> **注意事項**：
> - `.env` 不進入版本控制（已在 `.gitignore`）
> - `ACS_CONNECTION_STRING` 結尾不要有多餘文字
> - `GEMINI_API_KEY` 必須大寫

### Vercel（前端環境變數）

在 Vercel Dashboard → **Settings** → **Environment Variables**：

| Key | Value | Environment |
|-----|-------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Azure Functions 的完整 URL | Production / Preview / Development |

---

## 4. Backend 部署（Azure Functions）

### 4.1 登入 Azure

```bash
az login
# 瀏覽器會開啟，選擇 Azure for Students 帳號登入
```

### 4.2 產生 requirements.txt

Azure Functions 使用 `requirements.txt` 安裝套件，每次 `pyproject.toml` 更新後需重新產生：

```bash
cd /path/to/fin-news
uv export --no-dev --no-hashes --output-file backend/requirements.txt
```

> 這個指令會把所有依賴（含遞移依賴）固定版本輸出，確保 Azure 安裝的套件版本與本地一致。

### 4.3 部署到 Azure Functions

```bash
cd backend
func azure functionapp publish fin-news-functions --python
```

**部署過程說明**：
1. `func` 工具打包 `backend/` 目錄下所有 Python 檔案與 `requirements.txt`
2. 上傳至 Azure（Kudu deployment engine）
3. Azure 在雲端執行 `pip install -r requirements.txt`
4. 重新啟動 Function App
5. 驗證 host 狀態（`/admin/host/status`）
6. 列出所有已註冊的 functions

**部署成功後應看到**：

```
[2026-05-17T04:31:00.322Z] The deployment was successful!
Functions in fin-news-functions:
    daily_pipeline_trigger - [timerTrigger]
    get_news - [httpTrigger]
    get_news_dates - [httpTrigger]
    get_unsubscribe - [httpTrigger]
    post_subscribe - [httpTrigger]
```

---

## 5. Frontend 部署（Vercel）

### 5.1 首次部署（一次性）

1. 前往 [vercel.com](https://vercel.com) → **New Project**
2. 連接 GitHub 並選擇 `fin-news` repo
3. 設定：
   - **Framework Preset**：Next.js
   - **Root Directory**：`frontend`
4. 新增環境變數 `NEXT_PUBLIC_API_BASE_URL`（見 Section 3）
5. 點 **Deploy**

部署完成後取得網址（例如 `https://fin-news-report.vercel.app`），回到 Azure Functions CORS 設定填入此網址。

### 5.2 後續更新

每次 push 到 `main` branch，Vercel 會自動重新部署，無需手動操作。

---

## 6. 驗證部署結果

執行 smoke test 腳本驗證所有服務是否正常串接：

```bash
cd /path/to/fin-news
uv run python scripts/smoke_test.py
```

**預期結果（17/17 通過）**：

```
[1] 環境變數檢查        ✅ 全部 6 個
[2] Azure Blob Storage  ✅ 寫入、讀取、刪除
[3] ACS                 ✅ Client 初始化
[4] Gemini API          ✅ 回應正常
[5] HTTP API            ✅ 全部 4 個端點
[6] Vercel              ✅ 手動確認
```

**個別端點手動測試**：

```bash
BASE=https://fin-news-functions-xxxx.japaneast-01.azurewebsites.net

# 查詢今日新聞（部署初期回傳 404 正常）
curl $BASE/api/news

# 查詢可用日期
curl $BASE/api/news/dates

# 訂閱
curl -X POST $BASE/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# 退訂
curl "$BASE/api/unsubscribe?email=test@example.com"
```

---

## 7. 日後更新部署

### Backend 有程式碼變更時

```bash
# 如果有新增/移除套件，先重新產生 requirements.txt
uv export --no-dev --no-hashes --output-file backend/requirements.txt

# 部署
cd backend
func azure functionapp publish fin-news-functions --python
```

### Frontend 有程式碼變更時

```bash
git add .
git commit -m "update frontend"
git push origin main
# Vercel 自動部署，約 1-2 分鐘完成
```

### 環境變數變更時

- **Azure Functions**：Azure Portal → Function App → **Environment variables** → 修改後 **Apply**，會自動重啟
- **Vercel**：Vercel Dashboard → **Settings** → **Environment Variables** → 修改後需手動 **Redeploy**

---

## 附錄：常見問題

| 問題 | 原因 | 解決方式 |
|------|------|---------|
| `API_KEY_SERVICE_BLOCKED` | Generative Language API 未啟用 | 到 GCP Console 啟用 API 或重建 API Key |
| `model not available to new users` | 模型名稱已棄用 | 改用 `gemini-2.5-flash` |
| `RequestDisallowedByAzure` | Azure for Students 地區限制 | 改選其他地區（East US、Japan East） |
| CORS error | Function App CORS 未設定 | 新增 Vercel URL 到 CORS Allowed Origins |
| `.env` 格式錯誤 | 多行值被合併 | 確認每個變數獨立一行，值不含多餘文字 |
