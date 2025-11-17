from typing import List, Dict
from input.robot import Robot
from input.group import Group
from input.migration_record import MigrationRecord
from main.function import Function


class Evalution:
    def __init__(self, id_to_robots: Dict[int, Robot], id_to_groups: Dict[int, Group]):
        self.id_to_robots = id_to_robots
        self.id_to_groups = id_to_groups
        self.function = Function(id_to_robots, id_to_groups)

    def calculate_migration_cost(self, shortest_path_dict: Dict, migration_records: List[MigrationRecord]) -> float:
        """Calculate total migration cost."""
        total = 0.0
        for record in migration_records:
            path_weight = shortest_path_dict.get((record.from_robot, record.to_robot), 0.0)
            total += path_weight
        return total

    def calculate_execute_tasks_cost(self, robots: List[Robot]) -> float:
        """Calculate total task execution cost."""
        total = 0.0
        for robot in robots:
            tasks_list = robot.tasks_list
            if tasks_list is not None:
                for task in tasks_list:
                    total += task.size / robot.capacity
        return total

    def calculate_mean_survival_rate(self, robots: List[Robot]) -> float:
        """Calculate mean survival rate."""
        total = 0.0
        count = 0
        for robot in robots:
            if robot.fault_a != 1:
                count += 1
            survival_rate = (1 - robot.fault_a) * (1 - robot.fault_o)
            total += survival_rate
        return total / count if count > 0 else 0.0
