import networkx as nx
from typing import List, Dict
from input.task import Task
from input.robot import Robot
from input.group import Group
from input.experiment_result import ExperimentResult
from main.initialize import Initialize
from evaluation.evalution import Evalution
from MPFTM.finder_leader import FinderLeader
from .opt_migration import OptMigration


class Opt:
    def __init__(self, tasks: List[Task], arc_graph: nx.Graph, robots: List[Robot],
                 a: float, b: float):
        self.tasks = tasks
        self.robots = robots
        self.arc_graph = arc_graph
        self.id_to_groups: Dict[int, Group] = {}
        self.id_to_robots: Dict[int, Robot] = {}
        self.shortest_path_dict: Dict = {}
        self.a = a
        self.b = b

    def opt_run(self) -> ExperimentResult:
        """Run optimization algorithm."""
        print("optRun")

        ini = Initialize()
        evalution = Evalution(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        for robot in self.robots:
            self.id_to_robots[robot.robot_id] = robot

        ini.run(self.tasks, self.robots, self.id_to_groups, self.id_to_robots)
        self._leader_selection(self.id_to_groups, self.id_to_robots, self.arc_graph)

        # Calculate all shortest paths
        self.shortest_path_dict = dict(nx.all_pairs_dijkstra_path_length(self.arc_graph, weight='weight'))

        opt_migration = OptMigration(
            self._convert_shortest_path_dict(), self.id_to_groups,
            self.id_to_robots, self.a, self.b
        )
        migration_records = opt_migration.run()

        sum_migration_cost = evalution.calculate_migration_cost(
            self._convert_shortest_path_dict(), migration_records
        )
        sum_execute_cost = evalution.calculate_execute_tasks_cost(self.robots)
        survival_rate = evalution.calculate_mean_survival_rate(self.robots)

        experiment_result.mean_execute_cost = sum_execute_cost
        experiment_result.mean_survival_rate = survival_rate
        experiment_result.mean_migration_cost = sum_migration_cost

        return experiment_result

    def _convert_shortest_path_dict(self) -> Dict:
        """Convert NetworkX shortest path dict to flat dict with (from, to) keys."""
        result = {}
        for source, targets in self.shortest_path_dict.items():
            for target, length in targets.items():
                result[(source, target)] = length
        return result

    def _leader_selection(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                         arc_graph: nx.Graph):
        """Select leader for each group."""
        finder = FinderLeader()
        for group in id_to_groups.values():
            if group.leader is None:
                group.leader = finder.find_leader(group, id_to_robots, id_to_groups,
                                                 arc_graph, self.a, self.b)

        # Add edges between leader nodes
        for group_id in id_to_groups.keys():
            leader_id = id_to_groups[group_id].leader.robot_id
            for to_group_id in id_to_groups.keys():
                to_leader_id = id_to_groups[to_group_id].leader.robot_id
                if group_id != to_group_id and not arc_graph.has_edge(leader_id, to_leader_id):
                    arc_graph.add_edge(leader_id, to_leader_id, weight=10)
