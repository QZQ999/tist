"""
Dynamic and stochastic disruption model.
Addresses reviewer concern Q3 about static disruption modeling.
"""
import random
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
import networkx as nx


class DisruptionType(Enum):
    """Types of disruptions in the supply chain."""
    NODE_FAILURE = "node_failure"  # Agent/facility fails
    LINK_FAILURE = "link_failure"  # Transportation route fails
    REGIONAL_DISASTER = "regional_disaster"  # Natural disaster affects area
    OVERLOAD = "overload"  # Capacity overload
    CASCADING = "cascading"  # Cascading failure propagation


class DisruptionSeverity(Enum):
    """Severity levels of disruptions."""
    MINOR = 1  # 20-40% capacity reduction
    MODERATE = 2  # 40-70% capacity reduction
    SEVERE = 3  # 70-100% capacity reduction


@dataclass
class DisruptionEvent:
    """Represents a disruption event."""
    event_id: int
    event_type: DisruptionType
    severity: DisruptionSeverity
    start_time: int
    duration: int  # Time steps until recovery
    affected_nodes: Set[int]
    affected_edges: Set[Tuple[int, int]]

    # Capacity reduction factor (0.0 = complete failure, 1.0 = no impact)
    capacity_factor: float = 0.0

    # Recovery progress (0.0 = not started, 1.0 = fully recovered)
    recovery_progress: float = 0.0

    def is_active(self, current_time: int) -> bool:
        """Check if disruption is currently active."""
        return self.start_time <= current_time < self.start_time + self.duration

    def get_current_capacity_factor(self, current_time: int) -> float:
        """
        Get current capacity factor considering partial recovery.

        Args:
            current_time: Current simulation time

        Returns:
            Capacity factor (0.0 to 1.0)
        """
        if not self.is_active(current_time):
            return 1.0

        # Linear recovery model
        time_since_start = current_time - self.start_time
        recovery_rate = 1.0 / self.duration if self.duration > 0 else 0.0
        self.recovery_progress = min(1.0, time_since_start * recovery_rate)

        # Capacity gradually recovers
        return self.capacity_factor + (1.0 - self.capacity_factor) * self.recovery_progress


class DynamicDisruptionGenerator:
    """
    Generates dynamic and stochastic disruption events.

    Supports:
    - Random disruption events with different probability distributions
    - Variable disruption durations
    - Cascading failures
    - Regional disasters
    """

    def __init__(self,
                 graph: nx.Graph,
                 num_nodes: int,
                 seed: int = 42):
        """
        Initialize disruption generator.

        Args:
            graph: Network graph
            num_nodes: Number of nodes in the network
            seed: Random seed for reproducibility
        """
        self.graph = graph
        self.num_nodes = num_nodes
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

        self.events: List[DisruptionEvent] = []
        self.event_counter = 0

    def generate_poisson_disruptions(self,
                                    time_horizon: int,
                                    lambda_rate: float = 0.05,
                                    severity_probs: Dict[DisruptionSeverity, float] = None) -> List[DisruptionEvent]:
        """
        Generate disruption events following a Poisson process.

        Args:
            time_horizon: Maximum simulation time
            lambda_rate: Average disruption rate (events per time step)
            severity_probs: Probability distribution over severity levels

        Returns:
            List of disruption events
        """
        if severity_probs is None:
            severity_probs = {
                DisruptionSeverity.MINOR: 0.6,
                DisruptionSeverity.MODERATE: 0.3,
                DisruptionSeverity.SEVERE: 0.1
            }

        events = []

        # Generate event times using Poisson process
        current_time = 0
        while current_time < time_horizon:
            # Inter-arrival time follows exponential distribution
            inter_arrival = np.random.exponential(1.0 / lambda_rate)
            current_time += int(inter_arrival)

            if current_time >= time_horizon:
                break

            # Generate disruption event
            event = self._generate_random_disruption(
                start_time=current_time,
                severity_probs=severity_probs
            )
            events.append(event)

        self.events.extend(events)
        return events

    def generate_regional_disaster(self,
                                   start_time: int,
                                   epicenter_node: int,
                                   radius: float,
                                   severity: DisruptionSeverity = DisruptionSeverity.SEVERE) -> DisruptionEvent:
        """
        Generate a regional disaster affecting multiple nodes.

        Args:
            start_time: When the disaster occurs
            epicenter_node: Center node of the disaster
            radius: Affected radius (in graph distance)
            severity: Severity level

        Returns:
            Disruption event
        """
        # Find all nodes within radius
        affected_nodes = set()
        affected_edges = set()

        try:
            # Use shortest path lengths from epicenter
            path_lengths = nx.single_source_shortest_path_length(
                self.graph, epicenter_node, cutoff=int(radius)
            )

            affected_nodes = set(path_lengths.keys())

            # Find affected edges
            for u, v in self.graph.edges():
                if u in affected_nodes or v in affected_nodes:
                    affected_edges.add((min(u, v), max(u, v)))

        except nx.NodeNotFound:
            # Fallback: just affect the epicenter
            affected_nodes.add(epicenter_node)

        # Duration based on severity
        duration = self._get_duration_from_severity(severity) * 2  # Regional disasters last longer

        # Capacity reduction based on severity
        capacity_factor = self._get_capacity_factor_from_severity(severity)

        event = DisruptionEvent(
            event_id=self.event_counter,
            event_type=DisruptionType.REGIONAL_DISASTER,
            severity=severity,
            start_time=start_time,
            duration=duration,
            affected_nodes=affected_nodes,
            affected_edges=affected_edges,
            capacity_factor=capacity_factor
        )

        self.event_counter += 1
        self.events.append(event)
        return event

    def generate_cascading_failure(self,
                                   initial_failed_node: int,
                                   start_time: int,
                                   propagation_prob: float = 0.3) -> List[DisruptionEvent]:
        """
        Generate cascading failure events.

        Args:
            initial_failed_node: Initially failed node
            start_time: Start time
            propagation_prob: Probability of failure propagating to neighbors

        Returns:
            List of cascading disruption events
        """
        events = []
        failed_nodes = {initial_failed_node}
        current_wave = {initial_failed_node}
        wave_time = start_time

        # Initial failure
        initial_event = DisruptionEvent(
            event_id=self.event_counter,
            event_type=DisruptionType.CASCADING,
            severity=DisruptionSeverity.SEVERE,
            start_time=start_time,
            duration=random.randint(10, 30),
            affected_nodes={initial_failed_node},
            affected_edges=set(),
            capacity_factor=0.1
        )
        self.event_counter += 1
        events.append(initial_event)

        # Propagate failure
        max_waves = 5
        for wave in range(max_waves):
            next_wave = set()

            for node in current_wave:
                # Check neighbors
                neighbors = list(self.graph.neighbors(node))
                for neighbor in neighbors:
                    if neighbor not in failed_nodes:
                        # Propagation probability
                        if random.random() < propagation_prob:
                            next_wave.add(neighbor)
                            failed_nodes.add(neighbor)

            if not next_wave:
                break

            # Create event for this wave
            wave_time += random.randint(1, 3)  # Delay between waves
            wave_event = DisruptionEvent(
                event_id=self.event_counter,
                event_type=DisruptionType.CASCADING,
                severity=DisruptionSeverity.MODERATE,  # Secondary failures are less severe
                start_time=wave_time,
                duration=random.randint(5, 15),
                affected_nodes=next_wave.copy(),
                affected_edges=set(),
                capacity_factor=0.3
            )
            self.event_counter += 1
            events.append(wave_event)

            current_wave = next_wave

        self.events.extend(events)
        return events

    def _generate_random_disruption(self,
                                   start_time: int,
                                   severity_probs: Dict[DisruptionSeverity, float]) -> DisruptionEvent:
        """Generate a random disruption event."""
        # Select severity
        severities = list(severity_probs.keys())
        probs = list(severity_probs.values())
        severity = np.random.choice(severities, p=probs)

        # Select disruption type
        disruption_types = [DisruptionType.NODE_FAILURE, DisruptionType.LINK_FAILURE]
        event_type = random.choice(disruption_types)

        # Generate affected nodes/edges
        affected_nodes = set()
        affected_edges = set()

        if event_type == DisruptionType.NODE_FAILURE:
            # Random node failure
            num_affected = random.randint(1, max(1, self.num_nodes // 10))
            affected_nodes = set(random.sample(range(self.num_nodes), min(num_affected, self.num_nodes)))

        elif event_type == DisruptionType.LINK_FAILURE:
            # Random link failure
            edges = list(self.graph.edges())
            num_affected = random.randint(1, max(1, len(edges) // 10))
            selected_edges = random.sample(edges, min(num_affected, len(edges)))
            affected_edges = {(min(u, v), max(u, v)) for u, v in selected_edges}

        # Duration based on severity
        duration = self._get_duration_from_severity(severity)

        # Capacity reduction based on severity
        capacity_factor = self._get_capacity_factor_from_severity(severity)

        event = DisruptionEvent(
            event_id=self.event_counter,
            event_type=event_type,
            severity=severity,
            start_time=start_time,
            duration=duration,
            affected_nodes=affected_nodes,
            affected_edges=affected_edges,
            capacity_factor=capacity_factor
        )

        self.event_counter += 1
        return event

    def _get_duration_from_severity(self, severity: DisruptionSeverity) -> int:
        """Get disruption duration based on severity."""
        if severity == DisruptionSeverity.MINOR:
            return random.randint(3, 8)
        elif severity == DisruptionSeverity.MODERATE:
            return random.randint(8, 20)
        else:  # SEVERE
            return random.randint(20, 50)

    def _get_capacity_factor_from_severity(self, severity: DisruptionSeverity) -> float:
        """Get capacity reduction factor based on severity."""
        if severity == DisruptionSeverity.MINOR:
            return random.uniform(0.6, 0.8)  # 20-40% reduction
        elif severity == DisruptionSeverity.MODERATE:
            return random.uniform(0.3, 0.6)  # 40-70% reduction
        else:  # SEVERE
            return random.uniform(0.0, 0.3)  # 70-100% reduction

    def get_active_disruptions(self, current_time: int) -> List[DisruptionEvent]:
        """Get all disruptions active at current time."""
        return [event for event in self.events if event.is_active(current_time)]

    def get_node_capacity_factor(self, node_id: int, current_time: int) -> float:
        """
        Get current capacity factor for a node considering all active disruptions.

        Args:
            node_id: Node ID
            current_time: Current time

        Returns:
            Effective capacity factor (minimum across all active disruptions)
        """
        active_disruptions = self.get_active_disruptions(current_time)

        # Find minimum capacity factor among all affecting disruptions
        min_factor = 1.0
        for event in active_disruptions:
            if node_id in event.affected_nodes:
                factor = event.get_current_capacity_factor(current_time)
                min_factor = min(min_factor, factor)

        return min_factor

    def get_edge_availability(self, edge: Tuple[int, int], current_time: int) -> bool:
        """
        Check if an edge is available at current time.

        Args:
            edge: Edge tuple (u, v)
            current_time: Current time

        Returns:
            True if edge is available
        """
        normalized_edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
        active_disruptions = self.get_active_disruptions(current_time)

        for event in active_disruptions:
            if normalized_edge in event.affected_edges:
                # Edge is disrupted
                return False

        return True
