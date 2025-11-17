"""
Heterogeneous agent model with multiple resource types.
Addresses reviewer concerns Q1 and Q4 about homogeneous resource assumptions.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set
import random


@dataclass
class ResourceType:
    """Represents a type of resource (e.g., storage, processing, transport)."""
    name: str
    unit: str  # e.g., 'GB', 'CPU cores', 'trucks'


@dataclass
class HeterogeneousAgent:
    """
    Agent with multiple heterogeneous resources.

    Extends the basic Robot/Agent model to support:
    - Multiple resource types with different capacities
    - Resource-specific constraints
    - Capability matching for tasks
    """
    agent_id: int
    location: int  # Node ID in the graph
    group_id: int

    # Multi-dimensional resources: resource_type -> (capacity, current_load)
    resources: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Capabilities: set of task types this agent can handle
    capabilities: Set[str] = field(default_factory=set)

    # Failure probability
    fault_prob: float = 0.0

    def __post_init__(self):
        """Initialize resource tracking."""
        for resource_name in self.resources:
            if 'current_load' not in self.resources[resource_name]:
                self.resources[resource_name]['current_load'] = 0.0

    def add_resource(self, resource_name: str, capacity: float):
        """Add a resource type to this agent."""
        self.resources[resource_name] = {
            'capacity': capacity,
            'current_load': 0.0
        }

    def can_handle_task(self, task: 'HeterogeneousTask') -> bool:
        """
        Check if agent has capability and resources to handle a task.

        Args:
            task: Task to check

        Returns:
            True if agent can handle the task
        """
        # Check capability match
        if task.required_capability and task.required_capability not in self.capabilities:
            return False

        # Check resource availability
        for resource_name, required_amount in task.resource_requirements.items():
            if resource_name not in self.resources:
                return False

            available = (self.resources[resource_name]['capacity'] -
                        self.resources[resource_name]['current_load'])

            if available < required_amount:
                return False

        return True

    def get_available_capacity(self, resource_name: str = None) -> float:
        """
        Get available capacity for a specific resource or aggregate.

        Args:
            resource_name: Specific resource to query, or None for aggregate

        Returns:
            Available capacity
        """
        if resource_name:
            if resource_name not in self.resources:
                return 0.0
            return (self.resources[resource_name]['capacity'] -
                   self.resources[resource_name]['current_load'])

        # Aggregate capacity (normalized average)
        if not self.resources:
            return 0.0

        total_utilization = 0.0
        for resource_name in self.resources:
            capacity = self.resources[resource_name]['capacity']
            load = self.resources[resource_name]['current_load']
            if capacity > 0:
                utilization = load / capacity
                total_utilization += (1.0 - utilization)

        return total_utilization / len(self.resources)

    def allocate_task(self, task: 'HeterogeneousTask') -> bool:
        """
        Allocate resources for a task.

        Args:
            task: Task to allocate

        Returns:
            True if allocation successful
        """
        if not self.can_handle_task(task):
            return False

        # Allocate resources
        for resource_name, required_amount in task.resource_requirements.items():
            self.resources[resource_name]['current_load'] += required_amount

        return True

    def release_task(self, task: 'HeterogeneousTask'):
        """
        Release resources allocated to a task.

        Args:
            task: Task to release
        """
        for resource_name, required_amount in task.resource_requirements.items():
            if resource_name in self.resources:
                self.resources[resource_name]['current_load'] -= required_amount
                # Ensure non-negative
                self.resources[resource_name]['current_load'] = max(
                    0.0, self.resources[resource_name]['current_load']
                )


@dataclass
class HeterogeneousTask:
    """
    Task with heterogeneous resource requirements.

    Extends basic Task model to support:
    - Multiple resource type requirements
    - Capability requirements
    - Priority levels
    """
    task_id: int
    size: float  # Overall size/complexity
    arrive_time: int

    # Resource requirements: resource_type -> amount
    resource_requirements: Dict[str, float] = field(default_factory=dict)

    # Required capability (e.g., 'processing', 'refrigeration')
    required_capability: str = None

    # Priority (1-5, higher is more important)
    priority: int = 1

    def get_total_resource_demand(self) -> float:
        """Calculate total resource demand across all types."""
        return sum(self.resource_requirements.values())


class HeterogeneousAgentPool:
    """Manages a pool of heterogeneous agents."""

    def __init__(self, agents: List[HeterogeneousAgent]):
        """
        Initialize agent pool.

        Args:
            agents: List of heterogeneous agents
        """
        self.agents = agents
        self.agent_dict = {agent.agent_id: agent for agent in agents}

    def find_capable_agents(self, task: HeterogeneousTask) -> List[HeterogeneousAgent]:
        """
        Find all agents that can handle a specific task.

        Args:
            task: Task to match

        Returns:
            List of capable agents
        """
        return [agent for agent in self.agents if agent.can_handle_task(task)]

    def get_agent(self, agent_id: int) -> HeterogeneousAgent:
        """Get agent by ID."""
        return self.agent_dict.get(agent_id)

    def get_agents_by_capability(self, capability: str) -> List[HeterogeneousAgent]:
        """Get all agents with a specific capability."""
        return [agent for agent in self.agents if capability in agent.capabilities]

    def get_agents_with_resource(self, resource_name: str) -> List[HeterogeneousAgent]:
        """Get all agents that have a specific resource type."""
        return [agent for agent in self.agents if resource_name in agent.resources]


def create_heterogeneous_agents_from_supply_chain(nodes, resource_types: List[str]) -> List[HeterogeneousAgent]:
    """
    Create heterogeneous agents from supply chain nodes.

    Args:
        nodes: List of SupplyChainNode objects
        resource_types: List of available resource types

    Returns:
        List of HeterogeneousAgent objects
    """
    agents = []

    for node in nodes:
        agent = HeterogeneousAgent(
            agent_id=node.node_id,
            location=node.node_id,
            group_id={'producer': 0, 'processor': 1, 'distributor': 2, 'retailer': 3}.get(node.layer, 0)
        )

        # Assign resources based on node type
        if node.layer == 'producer':
            # Producers have high production capacity
            agent.add_resource('production', node.capacity * 1.2)
            agent.add_resource('storage', node.capacity * 0.6)
            agent.capabilities.add('produce')

        elif node.layer == 'processor':
            # Processors have processing and storage
            agent.add_resource('processing', node.capacity * 1.0)
            agent.add_resource('storage', node.capacity * 0.8)
            agent.add_resource('transport', node.capacity * 0.4)
            agent.capabilities.update(['process', 'store'])

        elif node.layer == 'distributor':
            # Distributors have high storage and transport
            agent.add_resource('storage', node.capacity * 1.5)
            agent.add_resource('transport', node.capacity * 1.0)
            agent.capabilities.update(['store', 'distribute'])

        elif node.layer == 'retailer':
            # Retailers have retail space and limited storage
            agent.add_resource('retail_space', node.capacity * 1.0)
            agent.add_resource('storage', node.capacity * 0.5)
            agent.capabilities.update(['sell', 'store'])

        # Add node-specific resources if available
        for res_type in node.resource_types:
            if res_type not in agent.resources:
                capacity = node.capacity * random.uniform(0.3, 0.7)
                agent.add_resource(res_type, capacity)

        agents.append(agent)

    return agents


def create_heterogeneous_tasks_from_supply_chain(tasks) -> List[HeterogeneousTask]:
    """
    Create heterogeneous tasks from supply chain tasks.

    Args:
        tasks: List of SupplyChainTask objects

    Returns:
        List of HeterogeneousTask objects
    """
    hetero_tasks = []

    for task in tasks:
        hetero_task = HeterogeneousTask(
            task_id=task.task_id,
            size=task.size,
            arrive_time=task.arrive_time,
            resource_requirements=task.resource_requirements.copy(),
            priority=task.priority
        )

        # Assign required capability based on product type
        capability_map = {
            'grain': 'process',
            'dairy': 'refrigeration',
            'meat': 'refrigeration',
            'vegetables': 'store',
            'fruits': 'store'
        }
        hetero_task.required_capability = capability_map.get(task.product_type, 'store')

        hetero_tasks.append(hetero_task)

    return hetero_tasks
