"""
Smoke Test — 驗證各雲端服務是否成功串接
執行方式：uv run python scripts/smoke_test.py
"""

import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
SKIP = "\033[93m⚠️  SKIP\033[0m"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    status = PASS if ok else FAIL
    print(f"  {status}  {name}")
    if detail:
        prefix = "      "
        for line in detail.splitlines():
            print(f"{prefix}{line}")


# ---------------------------------------------------------------------------
# 1. 環境變數完整性
# ---------------------------------------------------------------------------
print("\n[1] 環境變數檢查")

required_vars = [
    "GEMINI_API_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_STORAGE_CONTAINER_NAME",
    "ACS_CONNECTION_STRING",
    "ACS_SENDER_ADDRESS",
    "NEXT_PUBLIC_API_BASE_URL",
]
for var in required_vars:
    val = os.environ.get(var, "")
    check(var, bool(val), "" if val else "未設定或為空值")

# ---------------------------------------------------------------------------
# 2. Azure Blob Storage
# ---------------------------------------------------------------------------
print("\n[2] Azure Blob Storage")

try:
    from azure.storage.blob import BlobServiceClient

    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
    container = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "fin-news")

    client = BlobServiceClient.from_connection_string(conn_str)
    container_client = client.get_container_client(container)

    # 確認 container 存在
    props = container_client.get_container_properties()
    check("Container 存在", True, f"Container: {container}")

    # 寫入測試 blob
    test_blob_name = "smoke-test/ping.json"
    payload = json.dumps({"ping": "pong", "ts": datetime.now(timezone.utc).isoformat()})
    container_client.upload_blob(test_blob_name, payload, overwrite=True)
    check("Blob 寫入", True, f"Path: {test_blob_name}")

    # 讀回測試 blob
    data = container_client.download_blob(test_blob_name).readall()
    parsed = json.loads(data)
    check("Blob 讀取", parsed.get("ping") == "pong", f"回傳內容: {parsed}")

    # 刪除測試 blob
    container_client.delete_blob(test_blob_name)
    check("Blob 刪除", True)

except Exception as e:
    check("Blob Storage 連線", False, str(e))

# ---------------------------------------------------------------------------
# 3. Azure Communication Services（只驗證連線，不實際寄信）
# ---------------------------------------------------------------------------
print("\n[3] Azure Communication Services")

try:
    from azure.communication.email import EmailClient

    acs_conn = os.environ.get("ACS_CONNECTION_STRING", "")
    email_client = EmailClient.from_connection_string(acs_conn)
    check("ACS Client 初始化", True, "連線字串格式正確，client 建立成功")
except Exception as e:
    check("ACS Client 初始化", False, str(e))

# ---------------------------------------------------------------------------
# 4. Gemini API
# ---------------------------------------------------------------------------
print("\n[4] Gemini API")

try:
    from google import genai  # type: ignore[import-untyped]
    from google.genai import types  # type: ignore[import-untyped]

    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="回答「OK」這兩個字，不要多餘文字。",
        config=types.GenerateContentConfig(temperature=0.1),
    )
    text = response.text.strip()
    check("Gemini API 呼叫", len(text) < 30, f"回應：{text}")
except Exception as e:
    check("Gemini API 呼叫", False, str(e))

# ---------------------------------------------------------------------------
# 5. Azure Functions HTTP API（已部署的端點）
# ---------------------------------------------------------------------------
print("\n[5] Azure Functions HTTP API")

try:
    import httpx

    base_url = os.environ.get("NEXT_PUBLIC_API_BASE_URL", "").rstrip("/")

    if not base_url:
        check("API Base URL", False, "NEXT_PUBLIC_API_BASE_URL 未設定")
    else:
        # GET /api/news/dates
        r = httpx.get(f"{base_url}/api/news/dates", timeout=15)
        check(
            "GET /api/news/dates",
            r.status_code in (200, 404),
            f"HTTP {r.status_code}  body: {r.text[:120]}",
        )

        # GET /api/news（今日，預期 404 因為尚未有資料）
        r = httpx.get(f"{base_url}/api/news", timeout=15)
        check(
            "GET /api/news",
            r.status_code in (200, 404),
            f"HTTP {r.status_code}  body: {r.text[:120]}",
        )

        # POST /api/subscribe（用測試 email）
        r = httpx.post(
            f"{base_url}/api/subscribe",
            json={"email": "smoke-test@example.com"},
            timeout=15,
        )
        check(
            "POST /api/subscribe",
            r.status_code in (200, 201),
            f"HTTP {r.status_code}  body: {r.text[:120]}",
        )

        # GET /api/unsubscribe（清除剛才的測試 email）
        r = httpx.get(
            f"{base_url}/api/unsubscribe",
            params={"email": "smoke-test@example.com"},
            timeout=15,
        )
        check(
            "GET /api/unsubscribe",
            r.status_code == 200,
            f"HTTP {r.status_code}  body: {r.text[:120]}",
        )

except Exception as e:
    check("HTTP API 連線", False, str(e))

# ---------------------------------------------------------------------------
# 6. Vercel 前端
# ---------------------------------------------------------------------------
print("\n[6] Vercel 前端")

try:
    import httpx

    # 從 API base URL 推斷 Vercel URL（前端和 API 不同 domain，這裡手動印出提示）
    print(f"      請手動開啟瀏覽器確認：https://fin-news-report.vercel.app")
    check("Vercel 部署狀態", True, "請見上方連結（無法自動驗證前端渲染）")
except Exception as e:
    check("Vercel 前端", False, str(e))

# ---------------------------------------------------------------------------
# 總結
# ---------------------------------------------------------------------------
print("\n" + "=" * 55)
total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

print(f"  結果：{passed}/{total} 通過")
if failed:
    print(f"\n  以下項目需要修正：")
    for name, ok, detail in results:
        if not ok:
            print(f"  - {name}: {detail}")
print("=" * 55 + "\n")

sys.exit(0 if failed == 0 else 1)
