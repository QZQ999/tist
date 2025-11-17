import networkx as nx
from typing import Dict
from input.group import Group
from input.robot import Robot
from input.potential_field import PotentialField
from main.function import Function


class CalculatePonField:
    def __init__(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                 arc_graph: nx.Graph, id_to_i: Dict[int, float], shortest_path_dict: Dict,
                 a: float, b: float):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph
        self.shortest_path_dict = shortest_path_dict
        self.a = a
        self.b = b
        self.id_to_i = id_to_i
        self.y = 0.005
        self.yn = 0.3
        self.xn = 0.1
        self.x = 0.01

    def calculate_intra_p(self) -> Dict[int, PotentialField]:
        """Calculate potential field for nodes (intra-group)."""
        intra_potential = {}

        # Calculate mean I value
        i_sum = sum(self.id_to_i.values())
        i_mean = i_sum / len(self.id_to_robots)

        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            p = PotentialField()

            # Set attractive potential field
            i_value = self.id_to_i[robot_id]
            p.pegra = -self.a * self._gain(i_value - i_mean)

            # Set repulsive potential field
            ro = 0.0
            neighbors = list(self.arc_graph.neighbors(robot_id))

            for neighbor_id in neighbors:
                target_robot = self.id_to_robots[neighbor_id]

                if target_robot.robot_id == robot_id:
                    continue

                if target_robot.group_id != robot.group_id:
                    continue

                if target_robot.fault_a == 1:
                    # Inversely proportional to distance to faulty node
                    weight = self.arc_graph[robot_id][neighbor_id]['weight']
                    ro += 1 / weight

            if robot.fault_a == 1:
                p.perep = float('inf') / 2
            elif ro != 0:
                p.perep = self.b * (self.y * 1 / ro) * (1 / ro)
            else:
                p.perep = 0.0

            intra_potential[robot_id] = p

            # Update overload fault condition
            function = Function(self.id_to_robots, self.id_to_groups)
            fault_o = 1 - function.calculate_over_load_is(self.id_to_robots[robot_id])
            robot.fault_o = fault_o

        return intra_potential

    def calculate_inter_p(self) -> Dict[int, PotentialField]:
        """Calculate potential field for network layer (inter-group)."""
        inter_potential = {}

        for group_id in self.id_to_groups.keys():
            group = self.id_to_groups[group_id]
            p = PotentialField()

            # Calculate attractive potential field for network layer
            p.pegra = self.a * self.xn * group.group_load

            # Calculate repulsive field for network layer
            fk = 0
            robot_id_in_group = group.robot_id_in_group
            for robot_id in robot_id_in_group:
                robot = self.id_to_robots[robot_id]
                if robot.fault_a == 1:
                    fk += 1

            nk = len(robot_id_in_group)
            if fk == nk:
                p.perep = float('inf') / 2
            else:
                p.perep = self.b * (self.yn * fk / (nk - fk))

            inter_potential[group_id] = p

        return inter_potential

    def _gain(self, x: float) -> float:
        """Gain function."""
        return x
