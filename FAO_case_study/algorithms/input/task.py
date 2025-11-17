from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: int = 0
    size: float = 0.0
    arrive_time: int = 0
