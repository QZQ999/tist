import time
from input.reader import Reader
from LTM.ltm import LTM
from MPFTM.mpftm import MPFTM
from evaluation.evaluation_etra_target import EvaluationEtraTarget


def print_experiment_result(a: float, b: float, robot_load_std: float, task_size_std: float,
                           mean_robot_capacity: float, mean_task_size: float, experiment_result):
    """Print experiment results."""
    mean_execute_cost = experiment_result.mean_execute_cost
    mean_migration_cost = experiment_result.mean_migration_cost
    mean_survival_rate = experiment_result.mean_survival_rate

    target_opt = calculate_target_opt(a, b, mean_execute_cost + mean_migration_cost, mean_survival_rate)

    print(f"meanExecuteCost: {mean_execute_cost}")
    print(f"meanMigrationCost: {mean_migration_cost}")
    print(f"meanSurvivalRate: {mean_survival_rate}")
    print(f"robotLoadStd: {robot_load_std}")
    print(f"taskSizeStd: {task_size_std}")
    print(f"meanRobotCapacity: {mean_robot_capacity}")
    print(f"meanTaskSize: {mean_task_size}")
    print(f"targetOpt: {target_opt}")


def calculate_target_opt(a: float, b: float, mean_cost: float, mean_survival_rate: float) -> float:
    """Calculate target optimization value."""
    return a * mean_cost - b * mean_survival_rate


def main():
    tasks_file = "Task24.txt"
    robot_file = "RobotsInformation4.txt"
    graph_file = "Graph4.txt"

    reader = Reader()

    # Test runtime
    a = 0.1
    b = 1 - a

    tasks = reader.read_file_to_tasks(tasks_file)
    arc_graph = reader.read_file_to_graph(graph_file)
    robots = reader.read_file_to_robots(robot_file)

    evaluation_etra_target = EvaluationEtraTarget()

    robot_capacity_std = evaluation_etra_target.calculate_robot_capacity_std(robots)
    task_size_std = evaluation_etra_target.calculate_task_size_std(tasks)

    mean_robot_capacity = evaluation_etra_target.calculate_mean_robot_capacity(robots)
    mean_task_size = evaluation_etra_target.calculate_mean_task_size(tasks)

    start_time = time.time()

    mpftm = MPFTM(tasks, arc_graph, robots, a, b)
    ltm = LTM(tasks, arc_graph, robots, a, b)
    experiment_result = ltm.greedy_run()

    end_time = time.time()

    print(f"程序运行时间: {int((end_time - start_time) * 1000)}ms")
    print_experiment_result(a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, experiment_result)

    print("*******************************")
    print("                               ")

    # Re-read tasks for second run
    tasks = reader.read_file_to_tasks(tasks_file)
    start_time = time.time()
    experiment_result_mpftm = mpftm.mpfm_run()
    end_time = time.time()

    print(f"程序运行时间: {int((end_time - start_time) * 1000)}ms")
    print_experiment_result(a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, experiment_result_mpftm)


if __name__ == "__main__":
    main()
