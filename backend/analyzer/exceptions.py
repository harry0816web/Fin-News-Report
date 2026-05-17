class GeminiQuotaError(Exception):
    """HTTP 429：API 配額超出"""


class GeminiAPIError(Exception):
    """HTTP 5xx 或連線失敗（重試後仍失敗）"""


class GeminiResponseParseError(Exception):
    """Gemini 回傳的 JSON 格式無效"""
