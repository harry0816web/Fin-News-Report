from difflib import SequenceMatcher

from fetcher.models import RawArticle


def _similarity(a: str, b: str) -> float:
    """計算兩個標題字串的相似度，使用 difflib.SequenceMatcher。回傳 [0.0, 1.0]。"""
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(
    articles: list[RawArticle],
    threshold: float = 0.8,
) -> list[RawArticle]:
    """
    移除標題相似度 >= threshold 的重複文章。
    演算法：
    1. 對輸入列表以 published_at 由新至舊排序
    2. 對每篇文章，計算其標題與 accepted 列表中所有文章的相似度
    3. 若最大相似度 >= threshold，略過此篇
    4. 否則加入 accepted
    5. 回傳 accepted（已由新至舊排序）
    """
    sorted_articles = sorted(articles, key=lambda a: a.published_at, reverse=True)
    accepted: list[RawArticle] = []

    for article in sorted_articles:
        if not accepted:
            accepted.append(article)
            continue

        max_sim = max(_similarity(article.title, acc.title) for acc in accepted)
        if max_sim < threshold:
            accepted.append(article)

    return accepted
