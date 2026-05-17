import logging
from datetime import datetime, timedelta, timezone

from analyzer.exceptions import GeminiAPIError, GeminiQuotaError
from analyzer.gemini_analyzer import GeminiAnalyzer
from deduplicator.deduplicator import deduplicate
from fetcher.rss_fetcher import fetch_all_sources
from notifier.email_notifier import EmailNotifier
from orchestrator.models import PipelineResult
from storage.abstract_storage import AbstractStorageClient
from storage.models import DailyDigest

_TW_TZ = timezone(timedelta(hours=8))


def run_daily_pipeline(
    storage: AbstractStorageClient,
    notifier: EmailNotifier,
    analyzer: GeminiAnalyzer,
) -> PipelineResult:
    """
    執行完整的每日新聞處理流程。
    回傳：PipelineResult（狀態、處理文章數、錯誤資訊）。
    """
    # Step 1: Fetch
    raw_articles = fetch_all_sources()
    if not raw_articles:
        logging.error("All RSS sources failed. Aborting pipeline.")
        return PipelineResult(status="failed", error_message="No articles fetched")

    # Step 2: Deduplicate
    deduped = deduplicate(raw_articles)
    logging.info("Deduplicated: %d → %d articles", len(raw_articles), len(deduped))

    # Step 3: Analyze
    try:
        analyzed = analyzer.analyze(deduped)
    except GeminiQuotaError:
        logging.warning("Gemini quota exceeded. Sending notice to subscribers.")
        subscribers = storage.get_subscribers()
        if subscribers:
            notifier.send_quota_exceeded_notice([s.email for s in subscribers])
        return PipelineResult(status="quota_exceeded")
    except GeminiAPIError as e:
        logging.error("Gemini API error after retries: %s", e)
        return PipelineResult(status="failed", error_message=str(e))

    # Step 4: Save
    now_tw = datetime.now(tz=_TW_TZ)
    digest = DailyDigest(
        date=now_tw.strftime("%Y-%m-%d"),
        generated_at=now_tw.isoformat(),
        article_count=len(analyzed),
        articles=analyzed,
    )
    storage.save_daily_digest(digest)

    # Step 5: Cleanup
    storage.cleanup_old_digests(keep_days=7)

    # Step 6: Send email
    subscribers = storage.get_subscribers()
    if not subscribers:
        logging.info("No subscribers, skipping email.")
    else:
        notifier.send_daily_digest(digest, [s.email for s in subscribers])

    # Step 7: Done
    return PipelineResult(status="success", article_count=len(analyzed))
