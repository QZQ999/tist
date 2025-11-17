import heapq
import networkx as nx
from typing import Dict, List
from input.group import Group
from input.robot import Robot


class FinderAdLeaders:
    def find_ad_leaders(self, group: Group, id_to_robots: Dict[int, Robot],
                       id_to_groups: Dict[int, Group], arc_graph: nx.Graph,
                       shortest_path_dict: Dict, a: float, b: float, max_size: int) -> List[Robot]:
        """Find backup leaders for a group."""
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
                    continue

                sub_graph.add_node(neighbor_id)
                if not sub_graph.has_edge(robot_id, neighbor_id):
                    weight = arc_graph[robot_id][neighbor_id]['weight']
                    sub_graph.add_edge(robot_id, neighbor_id, weight=weight)

        # Calculate betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(sub_graph, weight='weight')

        # Select backup nodes - backup nodes enter priority queue sorted by ref value
        # I = b / (1 - (1 - FA)(1 - FO))
        # ref = b * d
        id_to_refmap = {}

        for robot_id in robot_id_set:
            robot = id_to_robots[robot_id]
            if robot.fault_a == 1:
                id_to_refmap[robot_id] = float('-inf')
                # Functional fault occurred, backup suitability is at minimum
            else:
                # betweenness_centrality + 1, so shortest path includes self to self, minimum betweenness centrality is 1
                # Add epsilon to avoid division by zero when fault_a and fault_o are both 0
                denominator = 1 - (1 - robot.fault_a) * (1 - robot.fault_o)
                if abs(denominator) < 1e-10:
                    denominator = 1e-10  # Small epsilon to prevent division by zero
                iscore = (betweenness_centrality.get(robot_id, 0.0) + 1) / denominator

                leader_id = group.leader.robot_id
                d = shortest_path_dict.get((leader_id, robot.robot_id), 100000.0)
                id_to_refmap[robot_id] = iscore * d

        # Priority queue: suitability from small to large
        ad_leaders_pq = []

        for robot_id in robot_id_set:
            ref_value = id_to_refmap[robot_id]
            if len(ad_leaders_pq) < max_size:
                heapq.heappush(ad_leaders_pq, (ref_value, robot_id))
            else:
                min_ref = ad_leaders_pq[0][0]
                if ref_value > min_ref:
                    heapq.heappop(ad_leaders_pq)
                    heapq.heappush(ad_leaders_pq, (ref_value, robot_id))

        return [id_to_robots[robot_id] for _, robot_id in ad_leaders_pq]
