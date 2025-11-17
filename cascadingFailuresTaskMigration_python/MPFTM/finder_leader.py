import networkx as nx
from typing import Dict
from input.group import Group
from input.robot import Robot
from main.function import Function


class FinderLeader:
    def find_leader(self, group: Group, id_to_robots: Dict[int, Robot],
                   id_to_groups: Dict[int, Group], arc_graph: nx.Graph,
                   a: float, b: float) -> Robot:
        """Find leader for a group based on betweenness centrality and survivability."""
        # Create subgraph for this group
        sub_graph = nx.Graph()
        robot_id_set = group.robot_id_in_group

        for robot_id in robot_id_set:
            sub_graph.add_node(robot_id)
            neighbors = list(arc_graph.neighbors(robot_id))

            for neighbor_id in neighbors:
                if neighbor_id == robot_id:
                    continue

                if id_to_robots[neighbor_id].group_id != group.group_id:
                    continue  # Don't add nodes from other layers (e.g., leader nodes connected to other leaders)

                sub_graph.add_node(neighbor_id)
                # Remove duplicate edges - only add if edge doesn't exist
                if not sub_graph.has_edge(robot_id, neighbor_id):
                    weight = arc_graph[robot_id][neighbor_id]['weight']
                    sub_graph.add_edge(robot_id, neighbor_id, weight=weight)

        # Calculate betweenness centrality for subgraph
        betweenness_centrality = nx.betweenness_centrality(sub_graph, weight='weight')

        leader_id = -1
        max_iscore = -1.0

        for _ in range(len(robot_id_set)):
            for vertex in robot_id_set:
                function = Function(id_to_robots, id_to_groups)
                bc_value = betweenness_centrality.get(vertex, 0.0)
                p = function.calculate_over_load_is(id_to_robots[vertex])
                iscore = a * bc_value * b * p
                if iscore > max_iscore:
                    max_iscore = iscore
                    leader_id = vertex

        return id_to_robots[leader_id]
