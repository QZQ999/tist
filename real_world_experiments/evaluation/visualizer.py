"""
Result visualization for real-world experiments.
Note: Visualization requires matplotlib. For now, we provide text-based reports.
"""
from typing import Dict, List
import sys


class TextVisualizer:
    """Text-based visualization for results."""

    def __init__(self):
        """Initialize visualizer."""
        pass

    def create_bar_chart_text(self,
                             data: Dict[str, float],
                             title: str,
                             max_width: int = 60):
        """
        Create a text-based bar chart.

        Args:
            data: Dictionary of label -> value
            title: Chart title
            max_width: Maximum bar width in characters
        """
        print(f"\n{title}")
        print("=" * 80)

        if not data:
            print("No data to display")
            return

        # Find max value for scaling
        max_value = max(data.values())
        if max_value == 0:
            max_value = 1.0

        # Print bars
        for label, value in data.items():
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            print(f"{label:<15} {bar} {value:.4f}")

        print("=" * 80)

    def create_comparison_table(self,
                               results: Dict[str, Dict],
                               metrics: List[str],
                               title: str = "Comparison Table"):
        """
        Create a text-based comparison table.

        Args:
            results: Dictionary of algorithm_name -> metrics_dict
            metrics: List of metric names to display
            title: Table title
        """
        print(f"\n{title}")
        print("=" * 100)

        # Header
        header = f"{'Algorithm':<15}"
        for metric in metrics:
            header += f" {metric:<12}"
        print(header)
        print("-" * 100)

        # Rows
        for alg_name, alg_results in results.items():
            row = f"{alg_name:<15}"
            for metric in metrics:
                value = alg_results.get(metric, 0.0)
                if isinstance(value, int):
                    row += f" {value:<12}"
                else:
                    row += f" {value:<12.4f}"
            print(row)

        print("=" * 100)

    def create_summary_report(self,
                            results: Dict[str, Dict],
                            a: float,
                            b: float):
        """
        Create a comprehensive summary report.

        Args:
            results: Dictionary of algorithm results
            a: Cost weight
            b: Survival rate weight
        """
        print("\n" + "="*100)
        print("EXPERIMENT SUMMARY REPORT")
        print("="*100)

        print(f"\nParameters: a={a:.2f}, b={b:.2f}")
        print(f"Number of algorithms tested: {len(results)}")

        # Find best in each category
        best_surv = max(results.items(), key=lambda x: x[1].get('surv_rate', 0))
        best_cost = min(results.items(), key=lambda x: x[1].get('total_cost', float('inf')))
        best_target = min(results.items(),
                         key=lambda x: a * x[1].get('total_cost', float('inf')) -
                                      b * x[1].get('surv_rate', 0))

        print("\nBest Performers:")
        print(f"  Highest Survival Rate: {best_surv[0]} ({best_surv[1].get('surv_rate', 0):.4f})")
        print(f"  Lowest Total Cost: {best_cost[0]} ({best_cost[1].get('total_cost', 0):.4f})")
        print(f"  Best Target Optimization: {best_target[0]}")

        # Performance ranges
        surv_rates = [r.get('surv_rate', 0) for r in results.values()]
        costs = [r.get('total_cost', 0) for r in results.values()]

        print("\nPerformance Ranges:")
        print(f"  Survival Rate: [{min(surv_rates):.4f}, {max(surv_rates):.4f}]")
        print(f"  Total Cost: [{min(costs):.4f}, {max(costs):.4f}]")

        # Runtime comparison
        runtimes = {name: r.get('runtime', 0) for name, r in results.items()}
        fastest = min(runtimes.items(), key=lambda x: x[1])
        slowest = max(runtimes.items(), key=lambda x: x[1])

        print("\nComputational Performance:")
        print(f"  Fastest: {fastest[0]} ({fastest[1]}ms)")
        print(f"  Slowest: {slowest[0]} ({slowest[1]}ms)")
        print(f"  Speedup: {slowest[1] / max(1, fastest[1]):.2f}x")

        print("="*100)


def print_scenario_header(scenario_name: str, description: str):
    """Print formatted scenario header."""
    print("\n" + "="*100)
    print(f"SCENARIO: {scenario_name}")
    print("="*100)
    print(description)
    print("="*100 + "\n")


def print_section_divider(section_name: str):
    """Print formatted section divider."""
    print("\n" + "-"*100)
    print(f"  {section_name}")
    print("-"*100 + "\n")
