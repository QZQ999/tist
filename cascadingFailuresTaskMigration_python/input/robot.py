from dataclasses import dataclass, field
from typing import List


@dataclass
class Robot:
    robot_id: int = 0
    capacity: float = 0.0
    load: float = 0.0
    tasks_list: List = field(default_factory=list)
    group_id: int = 0
    fault_a: float = 0.0
    fault_o: float = 0.0
    fault_s: float = 0.0
