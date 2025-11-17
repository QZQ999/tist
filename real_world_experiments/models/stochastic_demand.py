"""
Stochastic demand model with time-varying task arrivals.
Addresses reviewer concern Q3 about demand uncertainty.
"""
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Callable
from enum import Enum


class DemandPattern(Enum):
    """Types of demand patterns."""
    CONSTANT = "constant"  # Constant rate
    SEASONAL = "seasonal"  # Periodic fluctuations
    TRENDING = "trending"  # Increasing/decreasing trend
    BURSTY = "bursty"  # Sudden spikes


@dataclass
class TaskArrival:
    """Represents a task arrival event."""
    task_id: int
    arrival_time: int
    size: float
    priority: int = 1
    urgent: bool = False


class StochasticDemandGenerator:
    """
    Generates stochastic task demand with various patterns.

    Supports:
    - Poisson arrivals
    - Seasonal patterns
    - Trending demand
    - Burst events
    - Variable task sizes
    """

    def __init__(self, seed: int = 42):
        """
        Initialize demand generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def generate_poisson_arrivals(self,
                                  time_horizon: int,
                                  base_rate: float = 0.5,
                                  size_mean: float = 15.0,
                                  size_std: float = 5.0) -> List[TaskArrival]:
        """
        Generate task arrivals following a Poisson process.

        Args:
            time_horizon: Maximum time
            base_rate: Average arrival rate (tasks per time unit)
            size_mean: Mean task size
            size_std: Standard deviation of task size

        Returns:
            List of task arrivals
        """
        arrivals = []
        task_id = 0

        current_time = 0.0
        while current_time < time_horizon:
            # Inter-arrival time follows exponential distribution
            inter_arrival = np.random.exponential(1.0 / base_rate)
            current_time += inter_arrival

            if current_time >= time_horizon:
                break

            # Generate task size from normal distribution
            size = max(1.0, np.random.normal(size_mean, size_std))

            arrival = TaskArrival(
                task_id=task_id,
                arrival_time=int(current_time),
                size=size,
                priority=random.randint(1, 5)
            )
            arrivals.append(arrival)
            task_id += 1

        return arrivals

    def generate_seasonal_arrivals(self,
                                   time_horizon: int,
                                   base_rate: float = 0.5,
                                   period: int = 24,
                                   amplitude: float = 0.3,
                                   size_mean: float = 15.0,
                                   size_std: float = 5.0) -> List[TaskArrival]:
        """
        Generate task arrivals with seasonal patterns.

        Args:
            time_horizon: Maximum time
            base_rate: Base arrival rate
            period: Period of seasonal cycle
            amplitude: Amplitude of seasonal variation (0-1)
            size_mean: Mean task size
            size_std: Standard deviation of task size

        Returns:
            List of task arrivals
        """
        arrivals = []
        task_id = 0

        current_time = 0.0
        while current_time < time_horizon:
            # Calculate time-varying rate with seasonal pattern
            seasonal_factor = 1.0 + amplitude * np.sin(2 * np.pi * current_time / period)
            current_rate = base_rate * seasonal_factor

            # Inter-arrival time
            inter_arrival = np.random.exponential(1.0 / max(0.01, current_rate))
            current_time += inter_arrival

            if current_time >= time_horizon:
                break

            # Generate task size
            size = max(1.0, np.random.normal(size_mean, size_std))

            arrival = TaskArrival(
                task_id=task_id,
                arrival_time=int(current_time),
                size=size,
                priority=random.randint(1, 5)
            )
            arrivals.append(arrival)
            task_id += 1

        return arrivals

    def generate_trending_arrivals(self,
                                   time_horizon: int,
                                   initial_rate: float = 0.3,
                                   trend_slope: float = 0.01,
                                   size_mean: float = 15.0,
                                   size_std: float = 5.0) -> List[TaskArrival]:
        """
        Generate task arrivals with an increasing/decreasing trend.

        Args:
            time_horizon: Maximum time
            initial_rate: Initial arrival rate
            trend_slope: Rate of change (positive = increasing, negative = decreasing)
            size_mean: Mean task size
            size_std: Standard deviation of task size

        Returns:
            List of task arrivals
        """
        arrivals = []
        task_id = 0

        current_time = 0.0
        while current_time < time_horizon:
            # Calculate time-varying rate with linear trend
            current_rate = max(0.01, initial_rate + trend_slope * current_time)

            # Inter-arrival time
            inter_arrival = np.random.exponential(1.0 / current_rate)
            current_time += inter_arrival

            if current_time >= time_horizon:
                break

            # Generate task size (also trending)
            trending_size_mean = size_mean * (1.0 + 0.5 * trend_slope * current_time)
            size = max(1.0, np.random.normal(trending_size_mean, size_std))

            arrival = TaskArrival(
                task_id=task_id,
                arrival_time=int(current_time),
                size=size,
                priority=random.randint(1, 5)
            )
            arrivals.append(arrival)
            task_id += 1

        return arrivals

    def generate_bursty_arrivals(self,
                                 time_horizon: int,
                                 base_rate: float = 0.3,
                                 burst_rate: float = 2.0,
                                 burst_probability: float = 0.1,
                                 burst_duration: int = 5,
                                 size_mean: float = 15.0,
                                 size_std: float = 5.0) -> List[TaskArrival]:
        """
        Generate task arrivals with burst events.

        Args:
            time_horizon: Maximum time
            base_rate: Normal arrival rate
            burst_rate: Arrival rate during bursts
            burst_probability: Probability of burst starting per time unit
            burst_duration: Duration of burst events
            size_mean: Mean task size
            size_std: Standard deviation of task size

        Returns:
            List of task arrivals
        """
        arrivals = []
        task_id = 0

        current_time = 0.0
        in_burst = False
        burst_end_time = 0.0

        while current_time < time_horizon:
            # Check if we should start a burst
            if not in_burst and random.random() < burst_probability:
                in_burst = True
                burst_end_time = current_time + burst_duration

            # Check if burst has ended
            if in_burst and current_time >= burst_end_time:
                in_burst = False

            # Select appropriate rate
            current_rate = burst_rate if in_burst else base_rate

            # Inter-arrival time
            inter_arrival = np.random.exponential(1.0 / current_rate)
            current_time += inter_arrival

            if current_time >= time_horizon:
                break

            # Generate task size (larger during bursts)
            if in_burst:
                size = max(1.0, np.random.normal(size_mean * 1.5, size_std * 1.2))
                priority = random.randint(3, 5)  # Higher priority during bursts
                urgent = True
            else:
                size = max(1.0, np.random.normal(size_mean, size_std))
                priority = random.randint(1, 5)
                urgent = False

            arrival = TaskArrival(
                task_id=task_id,
                arrival_time=int(current_time),
                size=size,
                priority=priority,
                urgent=urgent
            )
            arrivals.append(arrival)
            task_id += 1

        return arrivals

    def generate_mixed_pattern_arrivals(self,
                                       time_horizon: int,
                                       base_rate: float = 0.5,
                                       seasonal_period: int = 24,
                                       seasonal_amplitude: float = 0.2,
                                       trend_slope: float = 0.005,
                                       burst_probability: float = 0.05,
                                       size_mean: float = 15.0,
                                       size_std: float = 5.0) -> List[TaskArrival]:
        """
        Generate task arrivals with mixed patterns (seasonal + trend + bursts).

        Args:
            time_horizon: Maximum time
            base_rate: Base arrival rate
            seasonal_period: Period of seasonal cycle
            seasonal_amplitude: Amplitude of seasonal variation
            trend_slope: Trend slope
            burst_probability: Probability of bursts
            size_mean: Mean task size
            size_std: Standard deviation of task size

        Returns:
            List of task arrivals
        """
        arrivals = []
        task_id = 0

        current_time = 0.0
        in_burst = False
        burst_end_time = 0.0

        while current_time < time_horizon:
            # Check burst status
            if not in_burst and random.random() < burst_probability:
                in_burst = True
                burst_end_time = current_time + random.randint(3, 8)

            if in_burst and current_time >= burst_end_time:
                in_burst = False

            # Calculate composite rate
            # Seasonal component
            seasonal_factor = 1.0 + seasonal_amplitude * np.sin(2 * np.pi * current_time / seasonal_period)

            # Trend component
            trend_factor = 1.0 + trend_slope * current_time

            # Burst component
            burst_factor = 2.5 if in_burst else 1.0

            # Combined rate
            current_rate = base_rate * seasonal_factor * trend_factor * burst_factor

            # Inter-arrival time
            inter_arrival = np.random.exponential(1.0 / max(0.01, current_rate))
            current_time += inter_arrival

            if current_time >= time_horizon:
                break

            # Generate task size
            size_multiplier = 1.5 if in_burst else 1.0
            size = max(1.0, np.random.normal(size_mean * size_multiplier, size_std))

            arrival = TaskArrival(
                task_id=task_id,
                arrival_time=int(current_time),
                size=size,
                priority=random.randint(3, 5) if in_burst else random.randint(1, 5),
                urgent=in_burst
            )
            arrivals.append(arrival)
            task_id += 1

        return arrivals

    def add_emergency_tasks(self,
                           arrivals: List[TaskArrival],
                           num_emergencies: int = 5,
                           time_horizon: int = 100) -> List[TaskArrival]:
        """
        Add emergency/urgent tasks to existing arrivals.

        Args:
            arrivals: Existing task arrivals
            num_emergencies: Number of emergency tasks to add
            time_horizon: Time horizon

        Returns:
            Updated list of arrivals including emergencies
        """
        max_existing_id = max([a.task_id for a in arrivals]) if arrivals else 0

        for i in range(num_emergencies):
            arrival_time = random.randint(0, time_horizon)
            size = random.uniform(20, 40)  # Larger emergency tasks

            emergency = TaskArrival(
                task_id=max_existing_id + i + 1,
                arrival_time=arrival_time,
                size=size,
                priority=5,  # Maximum priority
                urgent=True
            )
            arrivals.append(emergency)

        # Re-sort by arrival time
        arrivals.sort(key=lambda x: x.arrival_time)

        # Reassign task IDs to maintain order
        for idx, arrival in enumerate(arrivals):
            arrival.task_id = idx

        return arrivals


def convert_arrivals_to_tasks(arrivals: List[TaskArrival], task_file: str = "Tasks_Stochastic.txt"):
    """
    Convert task arrivals to task file format.

    Args:
        arrivals: List of task arrivals
        task_file: Output file path
    """
    with open(task_file, 'w') as f:
        for arrival in arrivals:
            f.write(f"{arrival.task_id}\t{arrival.size:.6f}\t{arrival.arrival_time}\n")


def main():
    """Test stochastic demand generation."""
    generator = StochasticDemandGenerator(seed=42)

    print("Generating different demand patterns...")

    # Pattern 1: Poisson arrivals
    print("\n1. Poisson arrivals:")
    poisson = generator.generate_poisson_arrivals(time_horizon=100, base_rate=0.5)
    print(f"   Generated {len(poisson)} tasks")

    # Pattern 2: Seasonal arrivals
    print("\n2. Seasonal arrivals:")
    seasonal = generator.generate_seasonal_arrivals(time_horizon=100, period=24, amplitude=0.3)
    print(f"   Generated {len(seasonal)} tasks")

    # Pattern 3: Trending arrivals
    print("\n3. Trending arrivals (increasing):")
    trending = generator.generate_trending_arrivals(time_horizon=100, trend_slope=0.01)
    print(f"   Generated {len(trending)} tasks")

    # Pattern 4: Bursty arrivals
    print("\n4. Bursty arrivals:")
    bursty = generator.generate_bursty_arrivals(time_horizon=100, burst_probability=0.1)
    print(f"   Generated {len(bursty)} tasks")
    urgent_count = sum(1 for a in bursty if a.urgent)
    print(f"   Urgent tasks: {urgent_count}")

    # Pattern 5: Mixed pattern
    print("\n5. Mixed pattern (seasonal + trend + bursts):")
    mixed = generator.generate_mixed_pattern_arrivals(time_horizon=100)
    print(f"   Generated {len(mixed)} tasks")

    # Export examples
    convert_arrivals_to_tasks(mixed, "Tasks_StochasticMixed.txt")
    print(f"\nExported mixed pattern to Tasks_StochasticMixed.txt")


if __name__ == "__main__":
    main()
