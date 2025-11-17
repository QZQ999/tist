import time
from typing import Dict, List
from input.reader import Reader
from input.task import Task
from input.robot import Robot
from LTM.ltm import LTM
from MPFTM.mpftm import MPFTM
from greedyPath.greedy_path import GreedyPath
from opt.opt import Opt
from evaluation.evaluation_etra_target import EvaluationEtraTarget
import networkx as nx


def print_experiment_result(algorithm_name: str, a: float, b: float,
                           robot_load_std: float, task_size_std: float,
                           mean_robot_capacity: float, mean_task_size: float,
                           experiment_result, runtime_ms: int):
    """Print experiment results for a specific algorithm."""
    mean_execute_cost = experiment_result.mean_execute_cost
    mean_migration_cost = experiment_result.mean_migration_cost
    mean_survival_rate = experiment_result.mean_survival_rate

    target_opt = calculate_target_opt(a, b, mean_execute_cost + mean_migration_cost, mean_survival_rate)

    print(f"\n{'='*60}")
    print(f"Algorithm: {algorithm_name}")
    print(f"{'='*60}")
    print(f"Runtime: {runtime_ms}ms")
    print(f"meanExecuteCost: {mean_execute_cost:.6f}")
    print(f"meanMigrationCost: {mean_migration_cost:.6f}")
    print(f"meanSurvivalRate: {mean_survival_rate:.6f}")
    print(f"robotLoadStd: {robot_load_std:.6f}")
    print(f"taskSizeStd: {task_size_std:.6f}")
    print(f"meanRobotCapacity: {mean_robot_capacity:.6f}")
    print(f"meanTaskSize: {mean_task_size:.6f}")
    print(f"targetOpt: {target_opt:.6f}")
    print(f"{'='*60}\n")


def calculate_target_opt(a: float, b: float, mean_cost: float, mean_survival_rate: float) -> float:
    """Calculate target optimization value."""
    return a * mean_cost - b * mean_survival_rate


def run_all_algorithms(tasks_file: str, robot_file: str, graph_file: str, a: float, b: float, run_opt: bool = False):
    """Run all benchmark algorithms and print comparison results."""
    reader = Reader()
    evaluation_etra_target = EvaluationEtraTarget()

    # Read initial data for statistics
    tasks_initial = reader.read_file_to_tasks(tasks_file)
    robots_initial = reader.read_file_to_robots(robot_file)

    robot_capacity_std = evaluation_etra_target.calculate_robot_capacity_std(robots_initial)
    task_size_std = evaluation_etra_target.calculate_task_size_std(tasks_initial)
    mean_robot_capacity = evaluation_etra_target.calculate_mean_robot_capacity(robots_initial)
    mean_task_size = evaluation_etra_target.calculate_mean_task_size(tasks_initial)

    # Store results for final comparison
    results = []

    print("\n" + "="*60)
    print("RUNNING ALL BENCHMARK ALGORITHMS")
    print("="*60)
    print(f"Task File: {tasks_file}")
    print(f"Robot File: {robot_file}")
    print(f"Graph File: {graph_file}")
    print(f"Parameters: a={a}, b={b}")
    print("="*60)

    # 1. Run CATM (LTM - Context-Aware Task Migration)
    print("\n[1/4] Running CATM (Context-Aware Task Migration)...")
    tasks = reader.read_file_to_tasks(tasks_file)
    arc_graph = reader.read_file_to_graph(graph_file)
    robots = reader.read_file_to_robots(robot_file)

    ltm = LTM(tasks, arc_graph, robots, a, b)
    start_time = time.time()
    result_ltm = ltm.greedy_run()
    end_time = time.time()
    runtime_ltm = int((end_time - start_time) * 1000)

    print_experiment_result("CATM (LTM)", a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, result_ltm, runtime_ltm)

    results.append(("CATM", result_ltm, runtime_ltm))

    # 2. Run KBTM (GreedyPath - Key-Based Task Migration)
    print("[2/4] Running KBTM (Key-Based Task Migration)...")
    tasks = reader.read_file_to_tasks(tasks_file)
    arc_graph = reader.read_file_to_graph(graph_file)
    robots = reader.read_file_to_robots(robot_file)

    greedy_path = GreedyPath(tasks, arc_graph, robots, a, b)
    start_time = time.time()
    result_greedy = greedy_path.greedy_run()
    end_time = time.time()
    runtime_greedy = int((end_time - start_time) * 1000)

    print_experiment_result("KBTM (GreedyPath)", a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, result_greedy, runtime_greedy)

    results.append(("KBTM", result_greedy, runtime_greedy))

    # 3. Run HCTM-MPF (MPFTM - Proposed Algorithm)
    print("[3/4] Running HCTM-MPF (Proposed Algorithm)...")
    tasks = reader.read_file_to_tasks(tasks_file)
    arc_graph = reader.read_file_to_graph(graph_file)
    robots = reader.read_file_to_robots(robot_file)

    mpftm = MPFTM(tasks, arc_graph, robots, a, b)
    start_time = time.time()
    result_mpftm = mpftm.mpfm_run()
    end_time = time.time()
    runtime_mpftm = int((end_time - start_time) * 1000)

    print_experiment_result("HCTM-MPF (MPFTM)", a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, result_mpftm, runtime_mpftm)

    results.append(("HCTM-MPF", result_mpftm, runtime_mpftm))

    # 4. Run OPT (Optimal Solution) - Optional due to high computational cost
    if run_opt:
        print("[4/4] Running OPT (Optimal Solution)...")
        print("WARNING: OPT uses backtracking and may take VERY long for large instances (exponential complexity)...")
        tasks = reader.read_file_to_tasks(tasks_file)
        arc_graph = reader.read_file_to_graph(graph_file)
        robots = reader.read_file_to_robots(robot_file)

        opt = Opt(tasks, arc_graph, robots, a, b)
        start_time = time.time()
        result_opt = opt.opt_run()
        end_time = time.time()
        runtime_opt = int((end_time - start_time) * 1000)

        print_experiment_result("OPT (Optimal)", a, b, robot_capacity_std, task_size_std,
                               mean_robot_capacity, mean_task_size, result_opt, runtime_opt)

        results.append(("OPT", result_opt, runtime_opt))
    else:
        print("\n[4/4] Skipping OPT (Optimal Solution) - use smaller dataset or set run_opt=True to enable")
        print("Note: OPT algorithm has exponential complexity and may take hours for 24+ tasks\n")

    # Print comparison table
    print_comparison_table(results, a, b)


def print_comparison_table(results, a: float, b: float):
    """Print a comparison table of all algorithms."""
    print("\n" + "="*100)
    print("COMPARISON TABLE OF ALL ALGORITHMS")
    print("="*100)
    print(f"{'Algorithm':<15} {'Runtime(ms)':<12} {'ExecCost':<12} {'MigrCost':<12} "
          f"{'SurvRate':<12} {'TotalCost':<12} {'TargetOpt':<12}")
    print("-"*100)

    for name, result, runtime in results:
        exec_cost = result.mean_execute_cost
        migr_cost = result.mean_migration_cost
        surv_rate = result.mean_survival_rate
        total_cost = exec_cost + migr_cost
        target_opt = calculate_target_opt(a, b, total_cost, surv_rate)

        print(f"{name:<15} {runtime:<12} {exec_cost:<12.4f} {migr_cost:<12.4f} "
              f"{surv_rate:<12.4f} {total_cost:<12.4f} {target_opt:<12.4f}")

    print("="*100)

    # Find best algorithm
    best_idx = min(range(len(results)),
                   key=lambda i: calculate_target_opt(a, b,
                                                      results[i][1].mean_execute_cost + results[i][1].mean_migration_cost,
                                                      results[i][1].mean_survival_rate))

    print(f"\nBest Algorithm: {results[best_idx][0]} (Lowest TargetOpt)")
    print("="*100 + "\n")


def main():
    """Main function to run all experiments."""
    # Configuration
    tasks_file = "Task24.txt"
    robot_file = "RobotsInformation4.txt"
    graph_file = "Graph4.txt"

    a = 0.1
    b = 1 - a

    # Run all algorithms (OPT disabled by default for large instances)
    # Set run_opt=True to include OPT algorithm (warning: may take very long time)
    run_all_algorithms(tasks_file, robot_file, graph_file, a, b, run_opt=False)

    # For testing OPT, use smaller dataset:
    # Example: run_all_algorithms("Task6.txt", "RobotsInformation2.txt", "Graph2.txt", a, b, run_opt=True)


if __name__ == "__main__":
    main()
