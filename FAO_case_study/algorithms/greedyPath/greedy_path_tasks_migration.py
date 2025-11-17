import networkx as nx
from typing import Dict, List
from input.group import Group
from input.robot import Robot
from input.task import Task
from input.migration_record import MigrationRecord


class GreedyPathTasksMigration:
    def __init__(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                 shortest_path_dict: Dict, arc_graph: nx.Graph):
        self.arc_graph = arc_graph
        self.shortest_path_dict = shortest_path_dict
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.records = []

    def task_migration(self) -> List[MigrationRecord]:
        """Execute task migration for greedy path algorithm."""
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            if robot.fault_a == 1:
                tfs = list(robot.tasks_list)
                for task in tfs:
                    robot_migrated = self._greedy_find_migrated_robot_by_path(robot)
                    self._execute_migration(robot, robot_migrated, task)
        return self.records

    def _greedy_find_migrated_robot_by_path(self, f_robot: Robot) -> Robot:
        """Find robot to migrate tasks to based on shortest path."""
        migrated_robot = Robot()
        neighbors = list(self.arc_graph.neighbors(f_robot.robot_id))
        min_path_weight = float('inf')

        for neighbor_id in neighbors:
            target_robot = self.id_to_robots[neighbor_id]

            if target_robot.group_id != f_robot.group_id:
                continue

            path_weight = self.shortest_path_dict.get(
                (f_robot.robot_id, target_robot.robot_id), float('inf')
            )

            if path_weight < min_path_weight and target_robot.fault_a != 1:
                min_path_weight = path_weight
                migrated_robot = target_robot

        return migrated_robot

    def _execute_migration(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Execute task migration."""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        # Update inter-layer load and task list if different groups
        if robot.group_id != robot_migrated.group_id:
            self._update_inter(robot, robot_migrated, migration_task)

        # Update intra-layer load and task list
        self._update_intra(robot, robot_migrated, migration_task)

        record = MigrationRecord()
        record.from_robot = robot.robot_id
        record.to_robot = robot_migrated.robot_id
        self.records.append(record)

    def _update_inter(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Update inter-group load."""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        group_id = robot.group_id
        group = self.id_to_groups[group_id]
        robot_migrated_group_id = robot_migrated.group_id
        migrated_group = self.id_to_groups[robot_migrated_group_id]

        group.group_load = group.group_load - migration_task.size
        migrated_group.group_load = migrated_group.group_load + migration_task.size

    def _update_intra(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Update intra-group load and task lists."""
        tasks_list = robot.tasks_list
        if migration_task in tasks_list:
            tasks_list.remove(migration_task)
        robot.load = robot.load - migration_task.size
        robot.tasks_list = tasks_list

        robot_migrated_task_list = robot_migrated.tasks_list
        if robot_migrated_task_list is None:
            robot_migrated_task_list = []

        robot_migrated_task_list.append(migration_task)
        robot_migrated.load = robot_migrated.load + migration_task.size
        robot_migrated.tasks_list = robot_migrated_task_list
