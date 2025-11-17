import heapq
from typing import List, Dict, Set
from input.task import Task
from input.robot import Robot
from input.group import Group
from .function import Function


class Initialize:
    def __init__(self):
        self.fault_p = 0.5

    def run(self, tasks: List[Task], robots: List[Robot],
            id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot]):
        """Initialize task assignment and fault conditions."""
        self._ini_task(tasks, robots, id_to_groups, id_to_robots)
        self._ini_fault(id_to_robots, id_to_groups)

    def _ini_fault(self, id_to_robots: Dict[int, Robot], id_to_groups: Dict[int, Group]):
        """Initialize fault conditions for robots."""
        size = len(id_to_robots)
        fault_size = int(size * self.fault_p)
        if fault_size == 0:
            fault_size += 1
        step = size // fault_size

        # 0.1 represents the proportion of nodes with functional faults in the system
        for i in range(size):
            robot = id_to_robots[i]
            if i % step == 1:
                # Set functional fault - can simulate cascading failure scenario
                robot.fault_a = 1.0
                group_id = robot.group_id
                group = id_to_groups[group_id]
                group.group_capacity = group.group_capacity - robot.capacity

            function = Function(id_to_robots, id_to_groups)
            fault_o = 1 - function.calculate_over_load_is(id_to_robots[i])
            robot.fault_o = fault_o

    def _ini_task(self, tasks: List[Task], robots: List[Robot],
                  id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot]):
        """Initialize task assignment to robots and groups."""
        # Assign tasks with arrive_time == -1 to groups and robots (as initial state)
        tasks_pre = []
        for task in tasks[:]:
            if task.arrive_time != -1:
                break
            else:
                tasks_pre.append(task)

        for task in tasks_pre:
            tasks.remove(task)

        # Sort tasks by size (descending) - assign largest tasks to robots with highest capacity
        tasks_pre.sort(key=lambda t: t.size, reverse=True)

        # Initialize robot-task matching
        # Priority queue: robots sorted by load/capacity ratio
        pq_robots = []
        robots.sort(key=lambda r: r.capacity, reverse=True)

        for robot in robots:
            # Update robots in group
            group_id = robot.group_id
            group = id_to_groups.get(group_id, Group())
            robot_id_in_group = group.robot_id_in_group
            if robot_id_in_group is None:
                robot_id_in_group = set()
                robot_id_in_group.add(robot.robot_id)
            else:
                robot_id_in_group.add(robot.robot_id)

            group.robot_id_in_group = robot_id_in_group
            group.group_id = group_id
            id_to_groups[group_id] = group

            self._update(tasks_pre, robot, id_to_groups)
            heapq.heappush(pq_robots, (robot.load / robot.capacity, robot.robot_id, robot))

        while tasks_pre:
            # Match all initial tasks
            _, _, robot = heapq.heappop(pq_robots)
            self._update(tasks_pre, robot, id_to_groups)
            heapq.heappush(pq_robots, (robot.load / robot.capacity, robot.robot_id, robot))

        # Fill in group capacity information
        for group_id in id_to_groups.keys():
            group = id_to_groups[group_id]
            robot_id_in_group = group.robot_id_in_group
            capacity_sum = 0.0
            for robot_id in robot_id_in_group:
                capacity_sum += id_to_robots[robot_id].capacity
            group.group_capacity = capacity_sum

    def _update(self, tasks_pre: List[Task], robot: Robot, id_to_groups: Dict[int, Group]):
        """Update robot and group with assigned task."""
        robot_tasks_list = robot.tasks_list
        if not tasks_pre:
            return

        robot_tasks_list.append(tasks_pre[0])
        # Update robot load - assign largest task to robot with smallest load
        robot.load = robot.load + tasks_pre[0].size

        group_id = robot.group_id
        # Update group load
        group = id_to_groups[group_id]
        group.group_load = group.group_load + tasks_pre[0].size
        group.group_id = group_id

        tasks_pre.pop(0)
        robot.tasks_list = robot_tasks_list
