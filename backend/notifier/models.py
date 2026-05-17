from dataclasses import dataclass, field


@dataclass
class SendResult:
    success_count: int
    failure_count: int
    errors: list[str] = field(default_factory=list)
