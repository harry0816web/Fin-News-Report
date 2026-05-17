from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    TECH_MARKET = "科技股市"
    MACRO_ECONOMY = "總體經濟"
    LISTED_COMPANY = "上市公司公告"
    INTERNATIONAL = "國際財經"


@dataclass
class AnalyzedArticle:
    id: str  # UUID 字串
    title: str
    url: str
    source: str
    published_at: str  # ISO 8601 帶時區
    category: str  # Category 枚舉值
    summary: str  # AI 繁體中文摘要
    impact_analysis: str  # AI 影響分析
    sentiment: str  # "positive" | "negative" | "neutral"
