import math
from typing import Dict
import networkx as nx


class Function:
    def __init__(self, id_to_robots: Dict, id_to_groups: Dict):
        self.id_to_robots = id_to_robots
        self.id_to_groups = id_to_groups

    def calculate_over_load_is(self, robot) -> float:
        """Calculate Individual Survivability."""
        load = robot.load
        # Get group survivability score
        gs = self._calculate_gs(self.id_to_groups[robot.group_id])
        # Survivability function
        return max(gs * (1 - self._sig(load / 60)), 0.3)

    def _calculate_gs(self, group) -> float:
        """Calculate Group Survivability."""
        group_load = group.group_load
        # Use sigmoid-like function for monotonically non-increasing function between 0-1
        size = len(group.robot_id_in_group)
        return max(1 - self._sig(group_load / (size * 200)), 0.6)

    def _sig(self, x: float) -> float:
        """Sigmoid function variant."""
        return (math.exp(math.log(x + 1)) - math.exp(-math.log(x + 1))) / \
               (math.exp(math.log(x + 1)) + math.exp(-math.log(x + 1)))

    def calculate_contextual_load(self, leader, robot, arc_graph: nx.Graph,
                                  shortest_path_dict: Dict, a: float, b: float) -> float:
        """Calculate contextual load of a robot."""
        f = a * robot.load / robot.capacity - b * self.calculate_over_load_is(robot)

        # Get domain F from connected edges
        neighbors = list(arc_graph.neighbors(robot.robot_id))
        domain_f = 0.0
        cost_sum = 0.0

        for neighbor_id in neighbors:
            target_robot = self.id_to_robots[neighbor_id]

            if target_robot.group_id != robot.group_id or target_robot.robot_id == robot.robot_id:
                continue

            # Sum of communication costs with connected edges
            cost_sum += arc_graph[robot.robot_id][neighbor_id]['weight']
            domain_f += a * target_robot.load / target_robot.capacity - b * self.calculate_over_load_is(target_robot)

        size = len(neighbors) + 1
        domain_num = size + 1

        # Add cost for inter-layer task migration
        path_weight = shortest_path_dict.get((leader.robot_id, robot.robot_id), float('inf'))
        cost_sum += path_weight

        # Load function
        return f + 0.1 * (domain_f / domain_num + cost_sum / size)
