import json
import logging
import time
import uuid
from typing import Any

from analyzer.exceptions import GeminiAPIError, GeminiQuotaError, GeminiResponseParseError
from analyzer.models import AnalyzedArticle
from analyzer.prompt_builder import SYSTEM_PROMPT, build_user_prompt
from fetcher.models import RawArticle

_REQUIRED_FIELDS = {
    "title",
    "url",
    "source",
    "published_at",
    "category",
    "summary",
    "impact_analysis",
    "sentiment",
}


class GeminiAnalyzer:
    def __init__(self, api_key: str, client: Any = None) -> None:
        self._api_key = api_key
        self._client = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        from google import genai  # type: ignore[import-untyped]
        from google.genai import types  # type: ignore[import-untyped]

        return genai.Client(api_key=self._api_key)

    def analyze(self, articles: list[RawArticle]) -> list[AnalyzedArticle]:
        """
        呼叫 Gemini Flash API，回傳分析後的文章列表。
        HTTP 429 → GeminiQuotaError
        HTTP 5xx / 連線失敗 → 重試最多 3 次（間隔 5 秒），仍失敗 → GeminiAPIError
        JSON 解析失敗 → GeminiResponseParseError
        """
        prompt = build_user_prompt(articles)
        client = self._get_client()

        from google.genai import types  # type: ignore[import-untyped]

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            system_instruction=SYSTEM_PROMPT,
        )

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config,
                )
                return self._parse_response(response)
            except GeminiQuotaError:
                raise
            except GeminiResponseParseError:
                raise
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    raise GeminiQuotaError(error_str) from e
                logging.warning("Gemini API attempt %d failed: %s", attempt + 1, e)
                last_error = e
                if attempt < 2:
                    time.sleep(5)

        raise GeminiAPIError(f"Gemini API failed after 3 retries: {last_error}") from last_error

    def _parse_response(self, response: Any) -> list[AnalyzedArticle]:
        try:
            text = response.text if hasattr(response, "text") else str(response)
            data = json.loads(text)
        except (json.JSONDecodeError, AttributeError) as e:
            raise GeminiResponseParseError(f"Failed to parse Gemini response: {e}") from e

        if not isinstance(data, list):
            raise GeminiResponseParseError("Expected JSON array at top level")

        results: list[AnalyzedArticle] = []
        for item in data:
            if not isinstance(item, dict):
                raise GeminiResponseParseError(f"Expected object, got {type(item)}")
            missing = _REQUIRED_FIELDS - item.keys()
            if missing:
                raise GeminiResponseParseError(f"Missing required fields: {missing}")
            results.append(
                AnalyzedArticle(
                    id=str(uuid.uuid4()),
                    title=item["title"],
                    url=item["url"],
                    source=item["source"],
                    published_at=item["published_at"],
                    category=item["category"],
                    summary=item["summary"],
                    impact_analysis=item["impact_analysis"],
                    sentiment=item["sentiment"],
                )
            )
        return results
