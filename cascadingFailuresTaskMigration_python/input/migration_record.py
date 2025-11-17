from dataclasses import dataclass
from typing import Optional


@dataclass
class MigrationRecord:
    from_robot: Optional[int] = None
    to_robot: Optional[int] = None
