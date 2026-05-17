from __future__ import annotations

import logging
import os
from itertools import islice
from pathlib import Path
from typing import Any
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
from notifier.models import SendResult
from storage.models import DailyDigest

_BATCH_SIZE = 50
_CATEGORIES = ["科技股市", "總體經濟", "上市公司公告", "國際財經"]
_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _chunk(lst: list[str], size: int):  # type: ignore[no-untyped-def]
    it = iter(lst)
    while batch := list(islice(it, size)):
        yield batch


class EmailNotifier:
    def __init__(
        self,
        acs_connection_string: str,
        sender_address: str,
        acs_client: Any = None,
    ) -> None:
        self._sender = sender_address
        self._connection_string = acs_connection_string
        self._acs_client = acs_client
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=True,
        )

    def _get_client(self) -> Any:
        if self._acs_client is not None:
            return self._acs_client
        from azure.communication.email import EmailClient  # type: ignore[import-untyped]

        return EmailClient.from_connection_string(self._connection_string)

    def _make_unsubscribe_url(self, email: str) -> str:
        base = os.environ.get("NEXT_PUBLIC_API_BASE_URL", "http://localhost:7071")
        return f"{base}/api/unsubscribe?email={quote(email)}"

    def send_daily_digest(self, digest: DailyDigest, recipients: list[str]) -> SendResult:
        grouped: dict[str, list[Any]] = {cat: [] for cat in _CATEGORIES}
        for article in digest.articles:
            if article.category in grouped:
                grouped[article.category].append(article)

        success_count = 0
        failure_count = 0
        errors: list[str] = []
        client = self._get_client()

        for batch in _chunk(recipients, _BATCH_SIZE):
            try:
                for recipient in batch:
                    html_content = self._jinja_env.get_template("daily_digest.html").render(
                        date=digest.date,
                        grouped_articles=grouped,
                        unsubscribe_url=self._make_unsubscribe_url(recipient),
                    )
                    message = {
                        "senderAddress": self._sender,
                        "recipients": {"to": [{"address": recipient}]},
                        "content": {
                            "subject": f"📊 台灣財經日報 {digest.date}",
                            "html": html_content,
                        },
                    }
                    client.begin_send(message)
                success_count += len(batch)
            except Exception as e:
                logging.error("Failed to send batch: %s", e)
                failure_count += len(batch)
                errors.append(str(e))

        return SendResult(
            success_count=success_count,
            failure_count=failure_count,
            errors=errors,
        )

    def send_quota_exceeded_notice(self, recipients: list[str]) -> SendResult:
        success_count = 0
        failure_count = 0
        errors: list[str] = []
        client = self._get_client()

        for batch in _chunk(recipients, _BATCH_SIZE):
            try:
                for recipient in batch:
                    html_content = self._jinja_env.get_template("quota_exceeded.html").render(
                        unsubscribe_url=self._make_unsubscribe_url(recipient),
                    )
                    message = {
                        "senderAddress": self._sender,
                        "recipients": {"to": [{"address": recipient}]},
                        "content": {
                            "subject": "📊 台灣財經日報 — 今日 API 配額已用盡",
                            "html": html_content,
                        },
                    }
                    client.begin_send(message)
                success_count += len(batch)
            except Exception as e:
                logging.error("Failed to send quota notice batch: %s", e)
                failure_count += len(batch)
                errors.append(str(e))

        return SendResult(
            success_count=success_count,
            failure_count=failure_count,
            errors=errors,
        )
