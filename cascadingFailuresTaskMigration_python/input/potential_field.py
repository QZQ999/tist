from dataclasses import dataclass
from typing import Optional


@dataclass
class PotentialField:
    pegra: Optional[float] = None
    perep: Optional[float] = None
