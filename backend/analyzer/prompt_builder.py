import json

from fetcher.models import RawArticle

SYSTEM_PROMPT = """
你是一位台灣財經分析師。你的工作是從每日新聞中篩選重要資訊並提供分析。
輸出語言：繁體中文。
"""

OUTPUT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "url": {"type": "string"},
            "source": {"type": "string"},
            "published_at": {"type": "string"},
            "category": {
                "type": "string",
                "enum": ["科技股市", "總體經濟", "上市公司公告", "國際財經"],
            },
            "summary": {"type": "string"},
            "impact_analysis": {"type": "string"},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
            },
        },
        "required": [
            "title",
            "url",
            "source",
            "published_at",
            "category",
            "summary",
            "impact_analysis",
            "sentiment",
        ],
    },
}


def build_user_prompt(articles: list[RawArticle]) -> str:
    """
    組裝送入 Gemini 的 user prompt。
    格式：JSON 陣列，每則包含 title、source、url、published_at、description。
    """
    articles_data = [
        {
            "title": a.title,
            "source": a.source,
            "url": a.url,
            "published_at": a.published_at.isoformat(),
            "description": a.description,
        }
        for a in articles
    ]

    schema_str = json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, indent=2)
    articles_str = json.dumps(articles_data, ensure_ascii=False, indent=2)

    return f"""以下是今日抓取的台灣財經新聞（共 {len(articles)} 則）：

{articles_str}

請執行以下任務：
1. 從上述新聞中挑選 10-15 則最重要的財經新聞
2. 每則新聞歸入以下四類之一：科技股市、總體經濟、上市公司公告、國際財經
3. 每則生成 2-3 段繁體中文摘要
4. 每則生成對台灣股市/科技業的潛在影響分析，並標記情緒（positive/negative/neutral）
5. 嚴格依照以下 JSON Schema 輸出，不要包含 markdown 程式碼區塊，直接輸出 JSON 陣列：

{schema_str}
"""
