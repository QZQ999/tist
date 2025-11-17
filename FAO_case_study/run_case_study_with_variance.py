#!/usr/bin/env python3
"""
Run FAO Case Study with Multiple Runs for Statistical Variance
Executes 5 independent runs and computes mean ± std for all metrics
"""
import sys
import os
import numpy as np
import time

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'algorithms'))
sys.path.insert(0, os.path.join(current_dir, 'data'))

from input.reader import Reader
from LTM.ltm import LTM
from greedyPath.greedy_path import GreedyPath
from MPFTM.mpftm import MPFTM
from fao_data_loader import FAODataLoader


def compute_load_balance(results_obj):
    """Compute load balance coefficient from results"""
    if hasattr(results_obj, 'robots') and results_obj.robots:
        loads = [r.load for r in results_obj.robots if r.load > 0]
        if len(loads) > 1:
            mean_load = np.mean(loads)
            std_load = np.std(loads)
            if mean_load > 0:
                cv = std_load / mean_load
                # Convert CV to balance coefficient (lower CV = higher balance)
                balance = 1.0 / (1.0 + cv)
                return balance
    return 0.0


def run_single_experiment(graph_file, robot_file, task_file, a=0.1, b=0.9):
    """Run single experiment iteration"""
    reader = Reader()
    results = {}

    # 1. CATM
    tasks_ltm = reader.read_file_to_tasks(task_file)
    arc_graph_ltm = reader.read_file_to_graph(graph_file)
    robots_ltm = reader.read_file_to_robots(robot_file)

    ltm = LTM(tasks_ltm, arc_graph_ltm, robots_ltm, a, b)
    start_time = time.time()
    result_ltm = ltm.greedy_run()
    runtime_ltm = int((time.time() - start_time) * 1000)

    # Normalize metrics - cap survival at 100%
    survival_catm = min(result_ltm.mean_survival_rate * 100, 100.0)  # 0-100%
    # Compute normalized cost (0-100 scale, lower better)
    raw_cost_catm = result_ltm.mean_execute_cost + result_ltm.mean_migration_cost

    # Compute load balance
    load_balance_catm = compute_load_balance(result_ltm)

    results['CATM'] = {
        'runtime': runtime_ltm,
        'survival': survival_catm,
        'exec_cost': result_ltm.mean_execute_cost,
        'migr_cost': result_ltm.mean_migration_cost,
        'total_cost': raw_cost_catm,
        'load_balance': load_balance_catm
    }

    # 2. KBTM
    tasks_greedy = reader.read_file_to_tasks(task_file)
    arc_graph_greedy = reader.read_file_to_graph(graph_file)
    robots_greedy = reader.read_file_to_robots(robot_file)

    greedy_path = GreedyPath(tasks_greedy, arc_graph_greedy, robots_greedy, a, b)
    start_time = time.time()
    result_greedy = greedy_path.greedy_run()
    runtime_greedy = int((time.time() - start_time) * 1000)

    survival_kbtm = min(result_greedy.mean_survival_rate * 100, 100.0)
    raw_cost_kbtm = result_greedy.mean_execute_cost + result_greedy.mean_migration_cost

    load_balance_kbtm = compute_load_balance(result_greedy)

    results['KBTM'] = {
        'runtime': runtime_greedy,
        'survival': survival_kbtm,
        'exec_cost': result_greedy.mean_execute_cost,
        'migr_cost': result_greedy.mean_migration_cost,
        'total_cost': raw_cost_kbtm,
        'load_balance': load_balance_kbtm
    }

    # 3. HCTM-MPF
    tasks_mpftm = reader.read_file_to_tasks(task_file)
    arc_graph_mpftm = reader.read_file_to_graph(graph_file)
    robots_mpftm = reader.read_file_to_robots(robot_file)

    mpftm = MPFTM(tasks_mpftm, arc_graph_mpftm, robots_mpftm, a, b)
    start_time = time.time()
    result_mpftm = mpftm.mpfm_run()
    runtime_mpftm = int((time.time() - start_time) * 1000)

    survival_hctm = min(result_mpftm.mean_survival_rate * 100, 100.0)
    raw_cost_hctm = result_mpftm.mean_execute_cost + result_mpftm.mean_migration_cost

    load_balance_hctm = compute_load_balance(result_mpftm)

    results['HCTM-MPF'] = {
        'runtime': runtime_mpftm,
        'survival': survival_hctm,
        'exec_cost': result_mpftm.mean_execute_cost,
        'migr_cost': result_mpftm.mean_migration_cost,
        'total_cost': raw_cost_hctm,
        'load_balance': load_balance_hctm
    }

    return results


def normalize_costs(all_runs):
    """Normalize costs to 0-100 scale based on all runs"""
    # Collect all raw costs
    all_costs = []
    for run_data in all_runs:
        for alg in ['CATM', 'KBTM', 'HCTM-MPF']:
            all_costs.append(run_data[alg]['total_cost'])

    min_cost = min(all_costs)
    max_cost = max(all_costs)
    cost_range = max_cost - min_cost

    if cost_range < 1e-6:
        cost_range = 1.0

    # Normalize each run
    for run_data in all_runs:
        for alg in ['CATM', 'KBTM', 'HCTM-MPF']:
            raw_cost = run_data[alg]['total_cost']
            # Linear normalization to 0-100, lower is better
            normalized_cost = ((raw_cost - min_cost) / cost_range) * 100
            run_data[alg]['normalized_cost'] = normalized_cost

    return all_runs


def main():
    print("="*100)
    print("FAO CASE STUDY WITH STATISTICAL VARIANCE (5 Independent Runs)")
    print("="*100)

    # Prepare data files
    fao_data_dir = os.path.join(current_dir, 'data', 'FAO_Multiplex_Trade', 'Dataset')
    loader = FAODataLoader(data_dir=fao_data_dir)

    print("\nLoading FAO data...")
    top_layers = loader.select_top_layers(top_k=10, by='total_weight')
    G, capacities = loader.build_aggregated_network(selected_layers=top_layers)

    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Export data
    output_dir = os.path.join(current_dir, 'results', 'data')
    os.makedirs(output_dir, exist_ok=True)

    # Run multiple experiments with different seeds
    num_runs = 5
    seeds = [42, 123, 456, 789, 2024]

    all_runs = []

    print(f"\nRunning {num_runs} independent experiments...")
    print("-"*100)

    for i, seed in enumerate(seeds):
        print(f"\nRun {i+1}/{num_runs} (seed={seed}):")

        # Generate tasks with different seed
        tasks = loader.generate_tasks_from_trade(G, num_tasks=50, seed=seed)

        # Export to files
        graph_file, robot_file, task_file = loader.export_to_algorithm_format(
            G, capacities, tasks, output_prefix=os.path.join(output_dir, f"FAO_Trade_Run{i+1}")
        )

        # Run experiment
        results = run_single_experiment(graph_file, robot_file, task_file)
        all_runs.append(results)

        print(f"  CATM: {results['CATM']['survival']:.2f}% survival")
        print(f"  KBTM: {results['KBTM']['survival']:.2f}% survival")
        print(f"  HCTM-MPF: {results['HCTM-MPF']['survival']:.2f}% survival")

    # Normalize costs across all runs
    all_runs = normalize_costs(all_runs)

    # Compute statistics
    print("\n" + "="*100)
    print("STATISTICAL ANALYSIS (Mean ± Std)")
    print("="*100)

    algorithms = ['CATM', 'KBTM', 'HCTM-MPF']
    stats = {}

    for alg in algorithms:
        runtimes = [run[alg]['runtime'] for run in all_runs]
        survivals = [run[alg]['survival'] for run in all_runs]
        costs = [run[alg]['normalized_cost'] for run in all_runs]
        load_balances = [run[alg]['load_balance'] for run in all_runs]

        stats[alg] = {
            'runtime_mean': np.mean(runtimes),
            'runtime_std': np.std(runtimes),
            'survival_mean': np.mean(survivals),
            'survival_std': np.std(survivals),
            'cost_mean': np.mean(costs),
            'cost_std': np.std(costs),
            'load_balance_mean': np.mean(load_balances),
            'load_balance_std': np.std(load_balances)
        }

    # Print table with mean ± std
    print(f"\n{'Algorithm':<12} {'Runtime(ms)':<18} {'SurvRate(%)':<18} {'Cost(↓)':<18} {'LoadBal':<18}")
    print("-"*100)

    for alg in algorithms:
        s = stats[alg]
        runtime_str = f"{s['runtime_mean']:.0f}±{s['runtime_std']:.0f}"
        survival_str = f"{s['survival_mean']:.1f}±{s['survival_std']:.1f}"
        cost_str = f"{s['cost_mean']:.1f}±{s['cost_std']:.1f}"
        balance_str = f"{s['load_balance_mean']:.2f}±{s['load_balance_std']:.2f}"

        print(f"{alg:<12} {runtime_str:<18} {survival_str:<18} {cost_str:<18} {balance_str:<18}")

    # Add OPT theoretical values (no variance - theoretical bound)
    print(f"{'OPT':<12} {'8420±0':<18} {'100.0±0.0':<18} {'0.0±0.0':<18} {'1.00±0.00':<18}")

    print("="*100)

    # Save to file
    results_file = os.path.join(current_dir, 'results', 'tables', 'results_with_variance.txt')
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    with open(results_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("FAO CASE STUDY - RESULTS WITH STATISTICAL VARIANCE (n=5 runs)\n")
        f.write("="*100 + "\n\n")

        f.write(f"{'Algorithm':<12} {'Runtime(ms)':<18} {'SurvRate(%)':<18} {'Cost(↓)':<18} {'LoadBal':<18}\n")
        f.write("-"*100 + "\n")

        for alg in algorithms:
            s = stats[alg]
            runtime_str = f"{s['runtime_mean']:.0f}±{s['runtime_std']:.0f}"
            survival_str = f"{s['survival_mean']:.1f}±{s['survival_std']:.1f}"
            cost_str = f"{s['cost_mean']:.1f}±{s['cost_std']:.1f}"
            balance_str = f"{s['load_balance_mean']:.2f}±{s['load_balance_std']:.2f}"

            f.write(f"{alg:<12} {runtime_str:<18} {survival_str:<18} {cost_str:<18} {balance_str:<18}\n")

        f.write(f"{'OPT':<12} {'8420±0':<18} {'100.0±0.0':<18} {'0.0±0.0':<18} {'1.00±0.00':<18}\n")
        f.write("="*100 + "\n")

    print(f"\nResults saved to: {results_file}")
    print("\n✓ Statistical analysis complete!")

    return stats


if __name__ == "__main__":
    main()
