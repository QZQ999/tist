from dataclasses import dataclass
from typing import Optional


@dataclass
class ExperimentResult:
    mean_migration_cost: Optional[float] = None
    mean_execute_cost: Optional[float] = None
    mean_survival_rate: Optional[float] = None
