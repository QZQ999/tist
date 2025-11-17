import networkx as nx
from typing import Dict, List
from input.group import Group
from input.robot import Robot


class AdLeadersReplace:
    def __init__(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                 arc_graph: nx.Graph):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph

    def run(self):
        """Replace failed leaders with backup leaders."""
        for group_id in self.id_to_groups.keys():
            group = self.id_to_groups[group_id]
            if group.leader.fault_a == 1:
                self._replace(group)

    def _replace(self, group: Group):
        """Replace leader with best backup leader."""
        ad_leaders = group.ad_leaders

        # Create subgraph
        sub_graph = nx.Graph()
        robot_id_set = group.robot_id_in_group

        for robot_id in robot_id_set:
            sub_graph.add_node(robot_id)
            neighbors = list(self.arc_graph.neighbors(robot_id))

            for neighbor_id in neighbors:
                if neighbor_id == robot_id:
                    continue

                if self.id_to_robots[neighbor_id].group_id != group.group_id:
                    continue

                sub_graph.add_node(neighbor_id)
                if not sub_graph.has_edge(robot_id, neighbor_id):
                    weight = self.arc_graph[robot_id][neighbor_id]['weight']
                    sub_graph.add_edge(robot_id, neighbor_id, weight=weight)

        # Calculate betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(sub_graph, weight='weight')

        # This I measures betweenness centrality
        replace_leader = ad_leaders[0]
        max_iscore = -1.0

        for ad_leader in ad_leaders:
            bc_value = betweenness_centrality.get(ad_leader.robot_id, 0.0)
            iscore = (bc_value + 1) / (1 - (1 - ad_leader.fault_a) * (1 - ad_leader.fault_o))
            if iscore > max_iscore:
                replace_leader = ad_leader
                max_iscore = iscore

        group.leader = replace_leader
        ad_leaders.remove(replace_leader)
        group.ad_leaders = ad_leaders
