from dataclasses import dataclass
from typing import Literal

PipelineStatus = Literal["success", "failed", "quota_exceeded"]


@dataclass
class PipelineResult:
    status: PipelineStatus
    article_count: int = 0
    error_message: str = ""
