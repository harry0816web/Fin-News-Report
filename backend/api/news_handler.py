from datetime import date as Date
from datetime import datetime, timedelta, timezone

from storage.abstract_storage import AbstractStorageClient

_TW_TZ = timezone(timedelta(hours=8))
_MAX_DAYS = 7


def handle_get_news(
    date_str: str | None,
    storage: AbstractStorageClient,
) -> tuple[int, dict]:  # type: ignore[type-arg]
    """
    回傳 (status_code, body) tuple。
    date_str 為 None 時，預設今日（台灣時間 UTC+8）。
    """
    if date_str is None:
        target_date = datetime.now(tz=_TW_TZ).date()
    else:
        try:
            target_date = Date.fromisoformat(date_str)
        except ValueError:
            return 400, {"error": "invalid date format"}

    today_tw = datetime.now(tz=_TW_TZ).date()
    if (today_tw - target_date).days > _MAX_DAYS:
        return 400, {"error": "date out of range"}

    digest = storage.get_daily_digest(target_date)
    if digest is None:
        return 404, {"error": "not found"}

    return 200, digest.to_dict()


def handle_get_news_dates(
    storage: AbstractStorageClient,
) -> tuple[int, dict]:  # type: ignore[type-arg]
    """
    回傳 (200, {"dates": ["YYYY-MM-DD", ...]})，由新至舊排序。
    """
    dates = storage.list_available_dates()
    return 200, {"dates": [str(d) for d in dates]}
