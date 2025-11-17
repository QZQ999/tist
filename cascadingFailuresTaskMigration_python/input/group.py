from dataclasses import dataclass, field
from typing import List, Set, Optional


@dataclass
class Group:
    group_id: int = 0
    group_load: float = 0.0
    leader: Optional['Robot'] = None
    robot_id_in_group: Set[int] = field(default_factory=set)
    assigned_tasks: List = field(default_factory=list)
    group_capacity: float = 0.0
    ad_leaders: List = field(default_factory=list)
