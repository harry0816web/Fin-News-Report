from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawArticle:
    title: str
    url: str
    source: str
    published_at: datetime
    description: str
