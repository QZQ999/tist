"""
Extended evaluation metrics for real-world experiments.
"""
import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ExtendedMetrics:
    """Extended evaluation metrics for real-world experiments."""
    # Basic metrics
    mean_execute_cost: float
    mean_migration_cost: float
    mean_survival_rate: float
    total_cost: float

    # Robustness metrics
    std_execute_cost: float = 0.0
    std_migration_cost: float = 0.0
    std_survival_rate: float = 0.0

    # Worst-case metrics
    worst_execute_cost: float = 0.0
    worst_migration_cost: float = 0.0
    worst_survival_rate: float = 0.0

    # Performance distribution
    median_survival_rate: float = 0.0
    percentile_25_survival_rate: float = 0.0
    percentile_75_survival_rate: float = 0.0

    # Computational metrics
    runtime_ms: int = 0
    memory_usage_mb: float = 0.0


class RobustnessEvaluator:
    """Evaluate algorithm robustness across multiple scenarios."""

    def __init__(self):
        """Initialize evaluator."""
        pass

    def evaluate_multiple_runs(self,
                               results: List[Dict],
                               a: float,
                               b: float) -> ExtendedMetrics:
        """
        Evaluate metrics across multiple runs.

        Args:
            results: List of result dictionaries from multiple runs
            a: Cost weight
            b: Survival rate weight

        Returns:
            Extended metrics
        """
        exec_costs = [r['exec_cost'] for r in results]
        migr_costs = [r['migr_cost'] for r in results]
        surv_rates = [r['surv_rate'] for r in results]
        total_costs = [r['total_cost'] for r in results]

        metrics = ExtendedMetrics(
            mean_execute_cost=np.mean(exec_costs),
            mean_migration_cost=np.mean(migr_costs),
            mean_survival_rate=np.mean(surv_rates),
            total_cost=np.mean(total_costs),

            std_execute_cost=np.std(exec_costs),
            std_migration_cost=np.std(migr_costs),
            std_survival_rate=np.std(surv_rates),

            worst_execute_cost=np.max(exec_costs),
            worst_migration_cost=np.max(migr_costs),
            worst_survival_rate=np.min(surv_rates),

            median_survival_rate=np.median(surv_rates),
            percentile_25_survival_rate=np.percentile(surv_rates, 25),
            percentile_75_survival_rate=np.percentile(surv_rates, 75),

            runtime_ms=int(np.mean([r.get('runtime', 0) for r in results]))
        )

        return metrics

    def calculate_robustness_score(self,
                                   metrics: ExtendedMetrics,
                                   a: float,
                                   b: float) -> float:
        """
        Calculate robustness score.

        A lower score indicates better robustness (lower variance).

        Args:
            metrics: Extended metrics
            a: Cost weight
            b: Survival rate weight

        Returns:
            Robustness score
        """
        # Coefficient of variation for costs
        cv_cost = metrics.std_execute_cost / max(0.01, metrics.mean_execute_cost)

        # Normalized std for survival rate
        normalized_std_surv = metrics.std_survival_rate

        # Robustness score (lower is better)
        robustness_score = a * cv_cost + b * normalized_std_surv

        return robustness_score


class ComparativeAnalyzer:
    """Perform comparative analysis between algorithms."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def compare_algorithms(self,
                          results_dict: Dict[str, ExtendedMetrics],
                          a: float = 0.1,
                          b: float = 0.9) -> Dict:
        """
        Compare multiple algorithms.

        Args:
            results_dict: Dictionary of algorithm_name -> ExtendedMetrics
            a: Cost weight
            b: Survival rate weight

        Returns:
            Comparison results
        """
        comparison = {
            'rankings': {},
            'improvements': {},
            'best_in_category': {}
        }

        # Rank by target optimization
        target_opts = {
            name: a * metrics.total_cost - b * metrics.mean_survival_rate
            for name, metrics in results_dict.items()
        }

        sorted_algs = sorted(target_opts.items(), key=lambda x: x[1])
        comparison['rankings']['target_opt'] = [name for name, _ in sorted_algs]

        # Rank by survival rate
        surv_rates = {name: metrics.mean_survival_rate for name, metrics in results_dict.items()}
        sorted_surv = sorted(surv_rates.items(), key=lambda x: x[1], reverse=True)
        comparison['rankings']['survival_rate'] = [name for name, _ in sorted_surv]

        # Rank by total cost
        total_costs = {name: metrics.total_cost for name, metrics in results_dict.items()}
        sorted_costs = sorted(total_costs.items(), key=lambda x: x[1])
        comparison['rankings']['total_cost'] = [name for name, _ in sorted_costs]

        # Best in each category
        comparison['best_in_category']['survival_rate'] = sorted_surv[0][0]
        comparison['best_in_category']['total_cost'] = sorted_costs[0][0]
        comparison['best_in_category']['target_opt'] = sorted_algs[0][0]

        # Calculate improvements over baseline (first algorithm)
        if len(results_dict) > 1:
            baseline_name = list(results_dict.keys())[0]
            baseline = results_dict[baseline_name]

            for name, metrics in results_dict.items():
                if name == baseline_name:
                    continue

                surv_improvement = ((metrics.mean_survival_rate - baseline.mean_survival_rate) /
                                   max(0.01, baseline.mean_survival_rate)) * 100

                cost_improvement = ((baseline.total_cost - metrics.total_cost) /
                                   max(0.01, baseline.total_cost)) * 100

                comparison['improvements'][name] = {
                    'survival_rate_pct': surv_improvement,
                    'total_cost_pct': cost_improvement
                }

        return comparison

    def print_comparison_report(self, comparison: Dict):
        """Print comparison report."""
        print("\n" + "="*80)
        print("COMPARATIVE ANALYSIS REPORT")
        print("="*80)

        print("\nRankings:")
        print(f"  Target Optimization: {' > '.join(comparison['rankings']['target_opt'])}")
        print(f"  Survival Rate: {' > '.join(comparison['rankings']['survival_rate'])}")
        print(f"  Total Cost: {' > '.join(comparison['rankings']['total_cost'])}")

        print("\nBest in Category:")
        for category, algorithm in comparison['best_in_category'].items():
            print(f"  {category}: {algorithm}")

        if comparison['improvements']:
            print("\nImprovements over Baseline:")
            for name, improvements in comparison['improvements'].items():
                print(f"  {name}:")
                print(f"    Survival Rate: {improvements['survival_rate_pct']:+.2f}%")
                print(f"    Total Cost: {improvements['total_cost_pct']:+.2f}%")

        print("="*80)
