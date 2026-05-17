from __future__ import annotations

from dataclasses import dataclass, field

from analyzer.models import AnalyzedArticle


@dataclass
class DailyDigest:
    date: str  # "YYYY-MM-DD"
    generated_at: str  # ISO 8601 帶時區
    article_count: int
    articles: list[AnalyzedArticle] = field(default_factory=list)

    def to_dict(self) -> dict:  # type: ignore[type-arg]
        return {
            "date": self.date,
            "generated_at": self.generated_at,
            "article_count": self.article_count,
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "url": a.url,
                    "source": a.source,
                    "published_at": a.published_at,
                    "category": a.category,
                    "summary": a.summary,
                    "impact_analysis": a.impact_analysis,
                    "sentiment": a.sentiment,
                }
                for a in self.articles
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DailyDigest":  # type: ignore[type-arg]
        articles = [
            AnalyzedArticle(
                id=item["id"],
                title=item["title"],
                url=item["url"],
                source=item["source"],
                published_at=item["published_at"],
                category=item["category"],
                summary=item["summary"],
                impact_analysis=item["impact_analysis"],
                sentiment=item["sentiment"],
            )
            for item in data.get("articles", [])
        ]
        return cls(
            date=data["date"],
            generated_at=data["generated_at"],
            article_count=data["article_count"],
            articles=articles,
        )


@dataclass
class Subscriber:
    email: str
    subscribed_at: str  # ISO 8601 帶時區
