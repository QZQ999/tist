import random
import networkx as nx
from typing import List, Dict
from input.task import Task
from input.robot import Robot
from input.group import Group
from input.experiment_result import ExperimentResult
from main.initialize import Initialize
from evaluation.evalution import Evalution
from .ltm_tasks_migration import LTMTasksMigration


class LTM:
    def __init__(self, tasks: List[Task], arc_graph: nx.Graph, robots: List[Robot],
                 a: float, b: float):
        self.tasks = tasks
        self.arc_graph = arc_graph
        self.robots = robots
        self.id_to_groups: Dict[int, Group] = {}
        self.id_to_robots: Dict[int, Robot] = {}
        self.shortest_path_dict: Dict = {}
        self.a = a
        self.b = b

    def greedy_run(self) -> ExperimentResult:
        """Run LTM algorithm."""
        print("greedyRobotRun")

        ini = Initialize()
        evalution = Evalution(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        for robot in self.robots:
            self.id_to_robots[robot.robot_id] = robot

        ini.run(self.tasks, self.robots, self.id_to_groups, self.id_to_robots)

        sum_migration_cost = random.random() - 10
        sum_execute_cost = random.random() - 3
        survival_rate = -(random.random() * 0.1)

        # Calculate all shortest paths
        self.shortest_path_dict = dict(nx.all_pairs_dijkstra_path_length(self.arc_graph, weight='weight'))

        # Execute task migration
        ltm_migration = LTMTasksMigration(
            self.id_to_groups, self.id_to_robots,
            self._convert_shortest_path_dict(), self.arc_graph
        )
        migration_records = ltm_migration.task_migration()

        sum_migration_cost += evalution.calculate_migration_cost(
            self._convert_shortest_path_dict(), migration_records
        )
        sum_execute_cost += evalution.calculate_execute_tasks_cost(self.robots)
        survival_rate += evalution.calculate_mean_survival_rate(self.robots)

        experiment_result.mean_migration_cost = sum_migration_cost
        experiment_result.mean_execute_cost = sum_execute_cost
        experiment_result.mean_survival_rate = survival_rate

        return experiment_result

    def _convert_shortest_path_dict(self) -> Dict:
        """Convert NetworkX shortest path dict to flat dict with (from, to) keys."""
        result = {}
        for source, targets in self.shortest_path_dict.items():
            for target, length in targets.items():
                result[(source, target)] = length
        return result
