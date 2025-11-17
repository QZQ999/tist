import math
from typing import List
from input.robot import Robot
from input.task import Task


class EvaluationEtraTarget:
    def calculate_robot_capacity_std(self, robots: List[Robot]) -> float:
        """Calculate standard deviation of robot capacities."""
        capacity_sum = sum(robot.capacity for robot in robots)
        mean = capacity_sum / len(robots)
        sum_sqr = sum((robot.capacity - mean) ** 2 for robot in robots)
        return math.sqrt(sum_sqr / len(robots))

    def calculate_task_size_std(self, tasks: List[Task]) -> float:
        """Calculate standard deviation of task sizes."""
        size_sum = sum(task.size for task in tasks)
        mean = size_sum / len(tasks)
        sum_sqr = sum((task.size - mean) ** 2 for task in tasks)
        return math.sqrt(sum_sqr / len(tasks))

    def calculate_mean_robot_capacity(self, robots: List[Robot]) -> float:
        """Calculate mean robot capacity."""
        capacity_sum = sum(robot.capacity for robot in robots)
        return capacity_sum / len(robots)

    def calculate_mean_task_size(self, tasks: List[Task]) -> float:
        """Calculate mean task size."""
        size_sum = sum(task.size for task in tasks)
        return size_sum / len(tasks)
