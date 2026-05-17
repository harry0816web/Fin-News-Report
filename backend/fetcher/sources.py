from dataclasses import dataclass


@dataclass
class RSSSource:
    name: str
    url: str
    max_articles: int = 30


RSS_SOURCES: list[RSSSource] = [
    RSSSource("經濟日報", "https://money.udn.com/rssfeed/news/1/1001?ch=money"),
    RSSSource("工商時報", "https://ctee.com.tw/feed"),
    RSSSource("鉅亨網", "https://feeds.cnyes.com/market/tw/news.xml"),
    RSSSource("MoneyDJ", "https://www.moneydj.com/rss/news.aspx"),
    RSSSource("Yahoo財經", "https://tw.news.yahoo.com/rss/finance"),
    RSSSource("科技新報", "https://technews.tw/feed/"),
]
