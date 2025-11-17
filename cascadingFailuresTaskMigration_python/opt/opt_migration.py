import copy
from typing import Dict, List
from input.group import Group
from input.robot import Robot
from input.task import Task
from input.migration_record import MigrationRecord
from evaluation.evalution import Evalution


class OptMigration:
    def __init__(self, shortest_path_dict: Dict, id_to_groups: Dict[int, Group],
                 id_to_robots: Dict[int, Robot], a: float, b: float):
        self.shortest_path_dict = shortest_path_dict
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.a = a
        self.b = b
        self.best_id_robots = None
        self.best_id_groups = None
        self.min_target_value = float('inf')
        self.task_to_robot = {}
        self.all_tasks = []

    def run(self) -> List[MigrationRecord]:
        """Run optimization algorithm to find best task allocation."""
        # Collect all tasks
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            self.all_tasks.extend(robot.tasks_list)

        # Create temporary copies
        id_to_robots_temp = self._robot_map_copy_org(self.id_to_robots)
        id_to_groups_temp = self._group_map_copy_org(self.id_to_groups)

        # Record original task-robot mapping
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            for task in robot.tasks_list:
                self.task_to_robot[task] = robot

        self.best_id_robots = self._robot_map_copy(self.id_to_robots)
        self.best_id_groups = self._group_map_copy(self.id_to_groups)

        self._backtrace(id_to_robots_temp, id_to_groups_temp, self.all_tasks, 0)

        # Calculate migration records based on best allocation
        ret = self._calculate_migration_record(self.best_id_robots)
        return ret

    def _backtrace(self, id_to_robots_temp: Dict, id_to_groups_temp: Dict,
                  all_tasks: List[Task], index: int):
        """Backtracking algorithm to find optimal task allocation."""
        if index == len(all_tasks):
            target_value = self._calculate_target_value(id_to_robots_temp, id_to_groups_temp)
            if target_value < self.min_target_value:
                self.best_id_groups = self._group_map_copy(id_to_groups_temp)
                self.best_id_robots = self._robot_map_copy(id_to_robots_temp)
                self.min_target_value = target_value
                print(f"{index} {self.min_target_value}")
            return

        for robot_id in id_to_robots_temp.keys():
            robot_temp = id_to_robots_temp[robot_id]
            if robot_temp.fault_a == 1:
                continue  # Faulty robots cannot receive tasks

            for i in range(index, len(all_tasks)):
                task = all_tasks[i]
                tasks_list = robot_temp.tasks_list
                tasks_list.append(task)
                robot_temp.tasks_list = tasks_list
                robot_temp.load = robot_temp.load + task.size

                self._backtrace(id_to_robots_temp, id_to_groups_temp, all_tasks, index + 1)

                tasks_list.remove(task)
                robot_temp.load = robot_temp.load - task.size

    def _calculate_target_value(self, id_to_robots_temp: Dict, id_to_groups_temp: Dict) -> float:
        """Calculate target optimization value."""
        temp_migration_records = self._calculate_migration_record(id_to_robots_temp)
        evalution = Evalution(id_to_robots_temp, id_to_groups_temp)

        survival_rate = evalution.calculate_mean_survival_rate(list(id_to_robots_temp.values()))
        execute_tasks_cost = evalution.calculate_execute_tasks_cost(list(id_to_robots_temp.values()))
        migration_cost = evalution.calculate_migration_cost(self.shortest_path_dict, temp_migration_records)

        return self.a * (execute_tasks_cost + migration_cost) - self.b * survival_rate

    def _calculate_migration_record(self, id_to_robots_temp: Dict) -> List[MigrationRecord]:
        """Calculate migration records by comparing with original allocation."""
        records = []
        for robot_id in self.id_to_robots.keys():
            robot_temp = id_to_robots_temp[robot_id]
            for task in robot_temp.tasks_list:
                if task in self.task_to_robot:
                    robot = self.task_to_robot[task]
                    if robot.robot_id != robot_id:
                        record = MigrationRecord()
                        record.from_robot = robot.robot_id
                        record.to_robot = robot_id
                        records.append(record)
        return records

    def _robot_map_copy_org(self, id_to_robots: Dict) -> Dict:
        """Create copy of robot map with reset loads."""
        id_to_robots_temp = {}
        for robot_id, robot in id_to_robots.items():
            robot_temp = Robot()
            robot_temp.load = 0.0
            robot_temp.tasks_list = []
            robot_temp.group_id = robot.group_id
            robot_temp.capacity = robot.capacity
            robot_temp.robot_id = robot_id
            robot_temp.fault_a = robot.fault_a
            robot_temp.fault_o = robot.fault_o
            robot_temp.fault_s = robot.fault_s
            id_to_robots_temp[robot_id] = robot_temp
        return id_to_robots_temp

    def _group_map_copy_org(self, id_to_groups: Dict) -> Dict:
        """Create copy of group map with reset loads."""
        id_to_groups_temp = {}
        for group_id, group in id_to_groups.items():
            group_temp = Group()
            group_temp.group_load = 0.0
            group_temp.group_capacity = group.group_capacity
            group_temp.leader = group.leader
            group_temp.group_id = group_id
            group_temp.robot_id_in_group = group.robot_id_in_group.copy()
            id_to_groups_temp[group_id] = group_temp
        return id_to_groups_temp

    def _robot_map_copy(self, id_to_robots: Dict) -> Dict:
        """Create full copy of robot map."""
        id_to_robots_temp = {}
        for robot_id, robot in id_to_robots.items():
            robot_temp = Robot()
            robot_temp.load = robot.load
            robot_temp.tasks_list = robot.tasks_list.copy()
            robot_temp.group_id = robot.group_id
            robot_temp.capacity = robot.capacity
            robot_temp.robot_id = robot_id
            robot_temp.fault_a = robot.fault_a
            robot_temp.fault_o = robot.fault_o
            robot_temp.fault_s = robot.fault_s
            id_to_robots_temp[robot_id] = robot_temp
        return id_to_robots_temp

    def _group_map_copy(self, id_to_groups: Dict) -> Dict:
        """Create full copy of group map."""
        id_to_groups_temp = {}
        for group_id, group in id_to_groups.items():
            group_temp = Group()
            group_temp.group_load = group.group_load
            group_temp.group_capacity = group.group_capacity
            group_temp.leader = group.leader
            group_temp.group_id = group_id
            group_temp.robot_id_in_group = group.robot_id_in_group.copy()
            id_to_groups_temp[group_id] = group_temp
        return id_to_groups_temp
