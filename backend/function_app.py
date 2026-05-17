import json
import logging
import os

import azure.functions as func
from api.news_handler import handle_get_news, handle_get_news_dates
from api.subscribe_handler import handle_subscribe, handle_unsubscribe
from storage.blob_storage import BlobStorageClient

app = func.FunctionApp()


def _storage() -> BlobStorageClient:
    return BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])


# ---------------------------------------------------------------------------
# HTTP Triggers
# ---------------------------------------------------------------------------


@app.route(route="news", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_news(req: func.HttpRequest) -> func.HttpResponse:
    date_str = req.params.get("date") or None
    storage = _storage()
    status, body = handle_get_news(date_str, storage)
    return func.HttpResponse(
        json.dumps(body, ensure_ascii=False),
        status_code=status,
        mimetype="application/json",
    )


@app.route(route="news/dates", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_news_dates(req: func.HttpRequest) -> func.HttpResponse:
    storage = _storage()
    status, body = handle_get_news_dates(storage)
    return func.HttpResponse(
        json.dumps(body, ensure_ascii=False),
        status_code=status,
        mimetype="application/json",
    )


@app.route(route="subscribe", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def post_subscribe(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    storage = _storage()
    status, resp = handle_subscribe(body, storage)
    return func.HttpResponse(
        json.dumps(resp, ensure_ascii=False),
        status_code=status,
        mimetype="application/json",
    )


@app.route(route="unsubscribe", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_unsubscribe(req: func.HttpRequest) -> func.HttpResponse:
    email = req.params.get("email", "")
    storage = _storage()
    status, resp = handle_unsubscribe(email, storage)
    return func.HttpResponse(
        json.dumps(resp, ensure_ascii=False),
        status_code=status,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# Timer Trigger（將在 M6 Orchestrator 完成後啟用完整版本）
# ---------------------------------------------------------------------------


@app.timer_trigger(
    schedule="0 0 1 * * *",
    arg_name="timer",
    run_on_startup=False,
)
def daily_pipeline_trigger(timer: func.TimerRequest) -> None:
    """每天 01:00 UTC = 09:00 台灣時間 執行。"""
    from analyzer.gemini_analyzer import GeminiAnalyzer
    from notifier.email_notifier import EmailNotifier
    from orchestrator.pipeline import run_daily_pipeline
    from storage.blob_storage import BlobStorageClient

    storage = BlobStorageClient(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
    notifier = EmailNotifier(
        acs_connection_string=os.environ["ACS_CONNECTION_STRING"],
        sender_address=os.environ["ACS_SENDER_ADDRESS"],
    )
    analyzer = GeminiAnalyzer(api_key=os.environ["GEMINI_API_KEY"])

    result = run_daily_pipeline(storage, notifier, analyzer)
    logging.info("Pipeline completed: %s", result)
