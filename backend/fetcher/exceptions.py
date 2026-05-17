class FetchError(Exception):
    """單一 RSS 來源抓取失敗"""

    def __init__(self, source_name: str, reason: str) -> None:
        self.source_name = source_name
        super().__init__(f"Failed to fetch {source_name}: {reason}")
