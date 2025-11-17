"""
FAO Multiplex Trade Network Data Loader.

Loads real-world food trade network data from FAO (Food and Agriculture Organization).
This dataset represents international trade relationships for various food products.

Dataset Description:
- 214 countries (nodes)
- 364 food products (layers)
- 318,346 trade connections
- Directed and weighted network
- Data from year 2010

Reference:
"Structural reducibility of multilayer networks"
M. De Domenico, V. Nicosia, A. Arenas, and V. Latora
Nature Communications 2015 6, 6864
"""
import os
import networkx as nx
import random
from typing import Dict, List, Tuple, Set
from pathlib import Path
from collections import defaultdict


class FAODataLoader:
    """Load and process FAO food trade network data."""

    def __init__(self, data_dir: str = None):
        """
        Initialize FAO data loader.

        Args:
            data_dir: Path to FAO data directory
        """
        if data_dir is None:
            # Default to FAO_Multiplex_Trade directory
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "FAO_Multiplex_Trade" / "Dataset"

        self.data_dir = Path(data_dir)
        self.nodes = {}  # node_id -> country_name
        self.layers = {}  # layer_id -> product_name
        self.edges = []  # list of (layer_id, from_node, to_node, weight)

        self._load_data()

    def _load_data(self):
        """Load all FAO data files."""
        # Load nodes (countries)
        nodes_file = self.data_dir / "fao_trade_nodes.txt"
        with open(nodes_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    node_id = int(parts[0])
                    country_name = parts[1].replace('_', ' ')
                    self.nodes[node_id] = country_name

        print(f"Loaded {len(self.nodes)} countries")

        # Load layers (products)
        layers_file = self.data_dir / "fao_trade_layers.txt"
        with open(layers_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    layer_id = int(parts[0])
                    product_name = parts[1].replace('_', ' ')
                    self.layers[layer_id] = product_name

        print(f"Loaded {len(self.layers)} product types")

        # Load edges (trade relationships)
        edges_file = self.data_dir / "fao_trade_multiplex.edges"
        with open(edges_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4:
                    layer_id = int(parts[0])
                    from_node = int(parts[1])
                    to_node = int(parts[2])
                    weight = float(parts[3])
                    self.edges.append((layer_id, from_node, to_node, weight))

        print(f"Loaded {len(self.edges)} trade connections")

    def get_layer_statistics(self) -> Dict:
        """Get statistics for each layer."""
        layer_stats = defaultdict(lambda: {
            'num_edges': 0,
            'total_weight': 0.0,
            'max_weight': 0.0,
            'nodes': set()
        })

        for layer_id, from_node, to_node, weight in self.edges:
            layer_stats[layer_id]['num_edges'] += 1
            layer_stats[layer_id]['total_weight'] += weight
            layer_stats[layer_id]['max_weight'] = max(layer_stats[layer_id]['max_weight'], weight)
            layer_stats[layer_id]['nodes'].add(from_node)
            layer_stats[layer_id]['nodes'].add(to_node)

        # Convert sets to counts
        result = {}
        for layer_id, stats in layer_stats.items():
            result[layer_id] = {
                'product': self.layers.get(layer_id, f'Layer_{layer_id}'),
                'num_edges': stats['num_edges'],
                'num_nodes': len(stats['nodes']),
                'total_weight': stats['total_weight'],
                'max_weight': stats['max_weight'],
                'avg_weight': stats['total_weight'] / stats['num_edges'] if stats['num_edges'] > 0 else 0
            }

        return result

    def select_top_layers(self, top_k: int = 10, by: str = 'total_weight') -> List[int]:
        """
        Select top K product layers by various criteria.

        Args:
            top_k: Number of layers to select
            by: Selection criterion ('total_weight', 'num_edges', 'num_nodes')

        Returns:
            List of selected layer IDs
        """
        stats = self.get_layer_statistics()

        # Sort by criterion
        sorted_layers = sorted(
            stats.items(),
            key=lambda x: x[1][by],
            reverse=True
        )

        selected = [layer_id for layer_id, _ in sorted_layers[:top_k]]

        print(f"\nTop {top_k} products by {by}:")
        for i, (layer_id, stat) in enumerate(sorted_layers[:top_k], 1):
            print(f"  {i}. {stat['product']}: {stat[by]:.2f} ({stat['num_edges']} edges, {stat['num_nodes']} countries)")

        return selected

    def build_aggregated_network(self, selected_layers: List[int] = None) -> Tuple[nx.DiGraph, Dict]:
        """
        Build aggregated trade network from selected layers.

        Args:
            selected_layers: List of layer IDs to include (None = all layers)

        Returns:
            Tuple of (NetworkX graph, node attributes dict)
        """
        if selected_layers is None:
            selected_layers = list(self.layers.keys())

        G = nx.DiGraph()

        # Add all nodes
        for node_id, country_name in self.nodes.items():
            G.add_node(node_id, name=country_name)

        # Aggregate edges from selected layers
        edge_weights = defaultdict(float)

        for layer_id, from_node, to_node, weight in self.edges:
            if layer_id in selected_layers:
                edge_weights[(from_node, to_node)] += weight

        # Add aggregated edges
        for (from_node, to_node), total_weight in edge_weights.items():
            G.add_edge(from_node, to_node, weight=total_weight)

        print(f"\nAggregated network:")
        print(f"  Nodes: {G.number_of_nodes()}")
        print(f"  Edges: {G.number_of_edges()}")
        print(f"  Density: {nx.density(G):.4f}")

        # Calculate node capacities based on trade volume
        node_capacities = self._calculate_node_capacities(G)

        return G, node_capacities

    def _calculate_node_capacities(self, G: nx.DiGraph) -> Dict[int, float]:
        """Calculate node capacities based on trade volume."""
        capacities = {}

        for node in G.nodes():
            # Capacity = total outgoing + incoming trade volume
            out_volume = sum(data['weight'] for _, _, data in G.out_edges(node, data=True))
            in_volume = sum(data['weight'] for _, _, data in G.in_edges(node, data=True))
            total_volume = out_volume + in_volume

            # Normalize to reasonable range (10-200)
            # Find max volume first
            capacities[node] = total_volume

        # Normalize
        if capacities:
            max_vol = max(capacities.values())
            min_vol = min(v for v in capacities.values() if v > 0) if any(v > 0 for v in capacities.values()) else 1

            for node in capacities:
                if capacities[node] == 0:
                    capacities[node] = 10.0  # Minimum capacity
                else:
                    # Log scale normalization to range [10, 200]
                    import math
                    normalized = 10 + 190 * (math.log(capacities[node] + 1) - math.log(min_vol + 1)) / \
                                 (math.log(max_vol + 1) - math.log(min_vol + 1))
                    capacities[node] = normalized

        return capacities

    def generate_tasks_from_trade(self,
                                  G: nx.DiGraph,
                                  num_tasks: int = 50,
                                  time_horizon: int = 100,
                                  seed: int = 42) -> List[Dict]:
        """
        Generate tasks based on trade patterns.

        Tasks represent trade orders/shipments that need to be processed.

        Args:
            G: Trade network graph
            num_tasks: Number of tasks to generate
            time_horizon: Maximum arrival time
            seed: Random seed

        Returns:
            List of task dictionaries
        """
        random.seed(seed)
        tasks = []

        # Get edges with weights for sampling
        edges_with_weights = [(u, v, data['weight']) for u, v, data in G.edges(data=True)]

        if not edges_with_weights:
            return tasks

        # Sample edges proportional to trade volume
        total_weight = sum(w for _, _, w in edges_with_weights)
        probabilities = [w / total_weight for _, _, w in edges_with_weights]

        for task_id in range(num_tasks):
            # Sample an edge (trade route)
            idx = random.choices(range(len(edges_with_weights)), weights=probabilities)[0]
            from_node, to_node, weight = edges_with_weights[idx]

            # Task size proportional to trade volume (with some randomness)
            base_size = min(weight / 1000, 50)  # Scale down large weights
            size = max(5.0, base_size * random.uniform(0.5, 1.5))

            # Random arrival time
            arrive_time = random.randint(0, time_horizon)

            task = {
                'task_id': task_id,
                'size': size,
                'arrive_time': arrive_time,
                'source': from_node,
                'destination': to_node,
                'trade_volume': weight
            }
            tasks.append(task)

        # Sort by arrival time
        tasks.sort(key=lambda t: t['arrive_time'])

        # Reassign task IDs to maintain order
        for i, task in enumerate(tasks):
            task['task_id'] = i

        return tasks

    def export_to_algorithm_format(self,
                                   G: nx.DiGraph,
                                   node_capacities: Dict[int, float],
                                   tasks: List[Dict],
                                   output_prefix: str = "FAO_Trade") -> Tuple[str, str, str]:
        """
        Export FAO data to format compatible with existing algorithms.

        IMPORTANT: Remaps node IDs to start from 0 (algorithms expect 0-based indexing).

        Args:
            G: Trade network graph
            node_capacities: Node capacity dict
            tasks: List of tasks
            output_prefix: Output file prefix

        Returns:
            Tuple of (graph_file, robot_file, task_file)
        """
        # Convert directed graph to undirected for algorithms first
        G_undirected = G.to_undirected()

        # Collect nodes that actually appear in edges (exclude isolated nodes)
        nodes_with_edges = set()
        for u, v in G_undirected.edges():
            nodes_with_edges.add(u)
            nodes_with_edges.add(v)

        # Create node ID mapping: FAO_ID -> Algorithm_ID (0-based)
        # IMPORTANT: Only map nodes that actually have edges
        sorted_nodes = sorted(nodes_with_edges)
        node_id_mapping = {old_id: new_id for new_id, old_id in enumerate(sorted_nodes)}

        print(f"\nNode ID remapping: {len(node_id_mapping)} nodes")
        print(f"  Original FAO nodes: {len(G.nodes())}")
        print(f"  Nodes with edges: {len(nodes_with_edges)}")
        print(f"  Isolated nodes removed: {len(G.nodes()) - len(nodes_with_edges)}")
        print(f"  Original range: [{min(sorted_nodes)}, {max(sorted_nodes)}]")
        print(f"  Remapped range: [0, {len(sorted_nodes)-1}]")

        # Export graph with remapped IDs
        graph_file = f"{output_prefix}_Graph.txt"
        with open(graph_file, 'w') as f:
            for u, v, data in G_undirected.edges(data=True):
                u_new = node_id_mapping[u]
                v_new = node_id_mapping[v]
                weight = data.get('weight', 1.0)
                # Normalize weight to reasonable distance (inverse relationship)
                # Higher trade volume = shorter distance
                distance = max(1.0, 1000.0 / (weight + 1))
                f.write(f"{u_new}\t{v_new}\t{distance:.6f}\n")

        # Export robots (countries as agents) with remapped IDs
        # IMPORTANT: Only export robots for nodes that exist in the graph
        robot_file = f"{output_prefix}_Robots.txt"
        with open(robot_file, 'w') as f:
            for old_id in sorted_nodes:
                if old_id in node_id_mapping:  # Only export if in graph
                    new_id = node_id_mapping[old_id]
                    capacity = node_capacities.get(old_id, 50.0)
                    # Group ID based on capacity (rough clustering)
                    if capacity < 50:
                        group_id = 0  # Low capacity
                    elif capacity < 100:
                        group_id = 1  # Medium capacity
                    elif capacity < 150:
                        group_id = 2  # High capacity
                    else:
                        group_id = 3  # Very high capacity

                    f.write(f"{new_id}\t{capacity:.6f}\t{group_id}\n")

        # Export tasks (task IDs already 0-based, no remapping needed)
        task_file = f"{output_prefix}_Tasks.txt"
        with open(task_file, 'w') as f:
            for task in tasks:
                f.write(f"{task['task_id']}\t{task['size']:.6f}\t{task['arrive_time']}\n")

        return graph_file, robot_file, task_file


def main():
    """Test FAO data loader."""
    print("="*80)
    print("FAO MULTIPLEX TRADE NETWORK DATA LOADER")
    print("="*80)

    loader = FAODataLoader()

    print("\n" + "="*80)
    print("LAYER STATISTICS")
    print("="*80)

    # Get top products by trade volume
    top_layers = loader.select_top_layers(top_k=10, by='total_weight')

    # Build aggregated network
    print("\n" + "="*80)
    print("BUILDING AGGREGATED NETWORK")
    print("="*80)

    G, capacities = loader.build_aggregated_network(selected_layers=top_layers)

    # Generate tasks
    print("\n" + "="*80)
    print("GENERATING TASKS")
    print("="*80)

    tasks = loader.generate_tasks_from_trade(G, num_tasks=50, seed=42)
    print(f"Generated {len(tasks)} tasks")
    print(f"  Average task size: {sum(t['size'] for t in tasks) / len(tasks):.2f}")

    # Export
    print("\n" + "="*80)
    print("EXPORTING DATA")
    print("="*80)

    graph_file, robot_file, task_file = loader.export_to_algorithm_format(
        G, capacities, tasks, output_prefix="FAO_Trade"
    )

    print(f"  Graph: {graph_file}")
    print(f"  Robots: {robot_file}")
    print(f"  Tasks: {task_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
