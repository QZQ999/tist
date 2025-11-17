"""
Realistic supply chain network generator that mimics FAO food supply chain structure.
Generates multi-layer networks with producers, processors, distributors, and retailers.
"""
import random
import networkx as nx
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SupplyChainNode:
    """Represents a node in the supply chain network."""
    node_id: int
    layer: str  # 'producer', 'processor', 'distributor', 'retailer'
    capacity: float
    location: Tuple[float, float]  # (latitude, longitude)
    resource_types: List[str]  # e.g., ['storage', 'transport', 'processing']


@dataclass
class SupplyChainTask:
    """Represents a task/order in the supply chain."""
    task_id: int
    size: float
    arrive_time: int
    product_type: str  # e.g., 'grain', 'dairy', 'meat'
    priority: int  # 1-5, higher is more urgent
    resource_requirements: Dict[str, float]  # resource type -> amount needed


class SupplyChainGenerator:
    """Generate realistic multi-layer supply chain networks."""

    def __init__(self, seed: int = 42):
        """
        Initialize the generator.

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        self.product_types = ['grain', 'dairy', 'meat', 'vegetables', 'fruits']
        self.resource_types = ['storage', 'transport', 'processing', 'refrigeration']

    def generate_network(self,
                        num_producers: int = 10,
                        num_processors: int = 8,
                        num_distributors: int = 6,
                        num_retailers: int = 12) -> Tuple[nx.Graph, List[SupplyChainNode]]:
        """
        Generate a multi-layer supply chain network.

        Args:
            num_producers: Number of producer nodes (e.g., farms)
            num_processors: Number of processor nodes (e.g., factories)
            num_distributors: Number of distributor nodes (e.g., warehouses)
            num_retailers: Number of retailer nodes (e.g., stores)

        Returns:
            Tuple of (network graph, list of nodes)
        """
        G = nx.Graph()
        nodes = []
        node_id = 0

        # Layer 1: Producers (farms, agricultural facilities)
        producers = []
        for i in range(num_producers):
            capacity = random.uniform(80, 150)  # High capacity for production
            location = (random.uniform(-90, 90), random.uniform(-180, 180))
            # Producers have specialized resources
            resource_types = random.sample(self.resource_types, k=random.randint(1, 2))

            node = SupplyChainNode(
                node_id=node_id,
                layer='producer',
                capacity=capacity,
                location=location,
                resource_types=resource_types
            )
            producers.append(node)
            nodes.append(node)
            G.add_node(node_id, **{'layer': 'producer', 'capacity': capacity})
            node_id += 1

        # Layer 2: Processors (factories, processing plants)
        processors = []
        for i in range(num_processors):
            capacity = random.uniform(100, 180)  # Higher capacity for processing
            location = (random.uniform(-90, 90), random.uniform(-180, 180))
            # Processors need processing and storage
            resource_types = random.sample(self.resource_types, k=random.randint(2, 3))

            node = SupplyChainNode(
                node_id=node_id,
                layer='processor',
                capacity=capacity,
                location=location,
                resource_types=resource_types
            )
            processors.append(node)
            nodes.append(node)
            G.add_node(node_id, **{'layer': 'processor', 'capacity': capacity})
            node_id += 1

        # Layer 3: Distributors (warehouses, distribution centers)
        distributors = []
        for i in range(num_distributors):
            capacity = random.uniform(120, 200)  # Large capacity for distribution
            location = (random.uniform(-90, 90), random.uniform(-180, 180))
            # Distributors need storage and transport
            resource_types = random.sample(self.resource_types, k=random.randint(2, 4))

            node = SupplyChainNode(
                node_id=node_id,
                layer='distributor',
                capacity=capacity,
                location=location,
                resource_types=resource_types
            )
            distributors.append(node)
            nodes.append(node)
            G.add_node(node_id, **{'layer': 'distributor', 'capacity': capacity})
            node_id += 1

        # Layer 4: Retailers (stores, markets)
        retailers = []
        for i in range(num_retailers):
            capacity = random.uniform(60, 120)  # Moderate capacity for retail
            location = (random.uniform(-90, 90), random.uniform(-180, 180))
            # Retailers mainly need storage
            resource_types = random.sample(self.resource_types, k=random.randint(1, 2))

            node = SupplyChainNode(
                node_id=node_id,
                layer='retailer',
                capacity=capacity,
                location=location,
                resource_types=resource_types
            )
            retailers.append(node)
            nodes.append(node)
            G.add_node(node_id, **{'layer': 'retailer', 'capacity': capacity})
            node_id += 1

        # Create edges between layers
        # Producers -> Processors
        for producer in producers:
            # Each producer connects to 2-4 processors
            num_connections = random.randint(2, min(4, len(processors)))
            connected_processors = random.sample(processors, num_connections)
            for processor in connected_processors:
                distance = self._calculate_distance(producer.location, processor.location)
                G.add_edge(producer.node_id, processor.node_id, weight=distance)

        # Processors -> Distributors
        for processor in processors:
            num_connections = random.randint(2, min(3, len(distributors)))
            connected_distributors = random.sample(distributors, num_connections)
            for distributor in connected_distributors:
                distance = self._calculate_distance(processor.location, distributor.location)
                G.add_edge(processor.node_id, distributor.node_id, weight=distance)

        # Distributors -> Retailers
        # Track which retailers have been connected
        connected_retailers_set = set()

        for distributor in distributors:
            num_connections = random.randint(3, min(6, len(retailers)))
            selected_retailers = random.sample(retailers, num_connections)
            for retailer in selected_retailers:
                distance = self._calculate_distance(distributor.location, retailer.location)
                G.add_edge(distributor.node_id, retailer.node_id, weight=distance)
                connected_retailers_set.add(retailer.node_id)

        # Ensure all retailers are connected (add edges for any isolated retailers)
        for retailer in retailers:
            if retailer.node_id not in connected_retailers_set:
                # Connect to a random distributor
                distributor = random.choice(distributors)
                distance = self._calculate_distance(distributor.location, retailer.location)
                G.add_edge(distributor.node_id, retailer.node_id, weight=distance)

        # Add some intra-layer connections for redundancy
        self._add_intra_layer_edges(G, producers)
        self._add_intra_layer_edges(G, processors)
        self._add_intra_layer_edges(G, distributors)

        return G, nodes

    def generate_tasks(self,
                      num_tasks: int = 50,
                      time_horizon: int = 100) -> List[SupplyChainTask]:
        """
        Generate realistic supply chain tasks (orders).

        Args:
            num_tasks: Number of tasks to generate
            time_horizon: Maximum arrival time

        Returns:
            List of supply chain tasks
        """
        tasks = []

        for i in range(num_tasks):
            size = random.uniform(5, 30)  # Task size
            arrive_time = random.randint(0, time_horizon)
            product_type = random.choice(self.product_types)
            priority = random.randint(1, 5)

            # Generate resource requirements based on product type
            num_resources = random.randint(1, 3)
            required_resources = random.sample(self.resource_types, num_resources)
            resource_requirements = {
                res: random.uniform(0.3, 1.5) for res in required_resources
            }

            task = SupplyChainTask(
                task_id=i,
                size=size,
                arrive_time=arrive_time,
                product_type=product_type,
                priority=priority,
                resource_requirements=resource_requirements
            )
            tasks.append(task)

        # Sort by arrival time
        tasks.sort(key=lambda t: t.arrive_time)

        return tasks

    def _calculate_distance(self, loc1: Tuple[float, float],
                           loc2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two locations."""
        return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5

    def _add_intra_layer_edges(self, G: nx.Graph, layer_nodes: List[SupplyChainNode]):
        """Add edges within a layer for redundancy."""
        if len(layer_nodes) < 2:
            return

        # Add 20% intra-layer connections
        num_connections = max(1, int(len(layer_nodes) * 0.2))

        for _ in range(num_connections):
            node1, node2 = random.sample(layer_nodes, 2)
            if not G.has_edge(node1.node_id, node2.node_id):
                distance = self._calculate_distance(node1.location, node2.location)
                G.add_edge(node1.node_id, node2.node_id, weight=distance)

    def export_to_format(self,
                        graph: nx.Graph,
                        nodes: List[SupplyChainNode],
                        tasks: List[SupplyChainTask],
                        output_prefix: str = "SupplyChain"):
        """
        Export supply chain data to the format used by existing algorithms.

        Args:
            graph: Supply chain network
            nodes: List of supply chain nodes
            tasks: List of supply chain tasks
            output_prefix: Prefix for output files
        """
        # Export graph
        graph_file = f"{output_prefix}_Graph.txt"
        with open(graph_file, 'w') as f:
            for u, v, data in graph.edges(data=True):
                weight = data.get('weight', 1.0)
                f.write(f"{u}\t{v}\t{weight:.6f}\n")

        # Export nodes as robots (agents)
        robot_file = f"{output_prefix}_Robots.txt"
        with open(robot_file, 'w') as f:
            for node in nodes:
                # Group ID based on layer
                group_map = {'producer': 0, 'processor': 1, 'distributor': 2, 'retailer': 3}
                group_id = group_map.get(node.layer, 0)
                f.write(f"{node.node_id}\t{node.capacity:.6f}\t{group_id}\n")

        # Export tasks
        task_file = f"{output_prefix}_Tasks.txt"
        with open(task_file, 'w') as f:
            for task in tasks:
                f.write(f"{task.task_id}\t{task.size:.6f}\t{task.arrive_time}\n")

        return graph_file, robot_file, task_file


def main():
    """Generate sample supply chain data."""
    generator = SupplyChainGenerator(seed=42)

    # Generate network
    print("Generating supply chain network...")
    graph, nodes = generator.generate_network(
        num_producers=10,
        num_processors=8,
        num_distributors=6,
        num_retailers=12
    )

    print(f"Generated network with {len(nodes)} nodes and {graph.number_of_edges()} edges")
    print(f"  Producers: 10")
    print(f"  Processors: 8")
    print(f"  Distributors: 6")
    print(f"  Retailers: 12")

    # Generate tasks
    print("\nGenerating tasks...")
    tasks = generator.generate_tasks(num_tasks=50, time_horizon=100)
    print(f"Generated {len(tasks)} tasks")

    # Export data
    print("\nExporting data...")
    graph_file, robot_file, task_file = generator.export_to_format(
        graph, nodes, tasks,
        output_prefix="SupplyChain"
    )

    print(f"Exported to:")
    print(f"  {graph_file}")
    print(f"  {robot_file}")
    print(f"  {task_file}")


if __name__ == "__main__":
    main()
