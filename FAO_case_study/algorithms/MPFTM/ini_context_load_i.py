import networkx as nx
from typing import Dict
from input.group import Group
from input.robot import Robot
from main.function import Function


class IniContextLoadI:
    def __init__(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                 arc_graph: nx.Graph, shortest_path_dict: Dict, id_to_i: Dict[int, float],
                 a: float, b: float):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph
        self.shortest_path_dict = shortest_path_dict
        self.id_to_i = id_to_i
        self.a = a
        self.b = b

    def run(self):
        """Initialize contextual load for all robots."""
        function = Function(self.id_to_robots, self.id_to_groups)

        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            group = self.id_to_groups[robot.group_id]
            i_value = function.calculate_contextual_load(
                group.leader, robot, self.arc_graph, self.shortest_path_dict, self.a, self.b
            )
            if i_value > 1000 or i_value < -1000:
                i_value = 1.0
            self.id_to_i[robot_id] = i_value
