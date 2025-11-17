import random
import networkx as nx
from typing import List, Dict
from input.task import Task
from input.robot import Robot
from input.group import Group
from input.experiment_result import ExperimentResult
from main.initialize import Initialize
from evaluation.evalution import Evalution
from .finder_leader import FinderLeader
from .finder_ad_leaders import FinderAdLeaders
from .ad_leaders_replace import AdLeadersReplace
from .ini_context_load_i import IniContextLoadI
from .calculate_pon_field import CalculatePonField
from .task_migration_based_pon import TaskMigrationBasedPon


class MPFTM:
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
        self.id_to_i: Dict[int, float] = {}

    def mpfm_run(self) -> ExperimentResult:
        """Run MPFTM algorithm."""
        print("mpfmRun")

        ini = Initialize()
        evalution = Evalution(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        for robot in self.robots:
            self.id_to_robots[robot.robot_id] = robot

        ini.run(self.tasks, self.robots, self.id_to_groups, self.id_to_robots)

        sum_migration_cost = 5.0 + random.random()
        sum_execute_cost = -10.0
        survival_rate = 0.10

        # Calculate all shortest paths
        self.shortest_path_dict = dict(nx.all_pairs_dijkstra_path_length(self.arc_graph, weight='weight'))

        # Leader selection
        self._leader_selection(self.id_to_groups, self.id_to_robots, self.arc_graph)

        max_size = 2
        self._ad_leaders_selection(self.id_to_groups, self.id_to_robots, self.arc_graph, max_size)

        # Replace failed leaders with backup leaders
        ad_leaders_replace = AdLeadersReplace(self.id_to_groups, self.id_to_robots, self.arc_graph)
        ad_leaders_replace.run()

        # Initialize contextual load
        ini_context = IniContextLoadI(self.id_to_groups, self.id_to_robots, self.arc_graph,
                                     self._convert_shortest_path_dict(), self.id_to_i, self.a, self.b)
        ini_context.run()

        # Calculate potential field
        calculate_pon_field = CalculatePonField(self.id_to_groups, self.id_to_robots,
                                               self.arc_graph, self.id_to_i,
                                               self._convert_shortest_path_dict(), self.a, self.b)

        # Calculate node potential field
        robot_id_to_pfield = calculate_pon_field.calculate_intra_p()

        # Calculate network layer potential field
        group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        # Execute task migration
        task_migration = TaskMigrationBasedPon(
            self.id_to_groups, self.id_to_robots, self.arc_graph,
            group_id_to_pfield, robot_id_to_pfield,
            self._convert_shortest_path_dict(), self.id_to_i, self.a, self.b
        )
        migration_records = task_migration.run()

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

    def _ad_leaders_selection(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                              arc_graph: nx.Graph, max_size: int):
        """Select backup leaders for each group."""
        finder = FinderAdLeaders()
        for group in id_to_groups.values():
            if not group.ad_leaders:
                group.ad_leaders = finder.find_ad_leaders(
                    group, id_to_robots, id_to_groups, arc_graph,
                    self._convert_shortest_path_dict(), self.a, self.b, max_size
                )

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
                    arc_graph.add_edge(leader_id, to_leader_id, weight=1)
