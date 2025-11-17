import math
import networkx as nx
from typing import Dict, List, Set
from input.group import Group
from input.robot import Robot
from input.task import Task
from input.potential_field import PotentialField
from input.migration_record import MigrationRecord
from .ini_context_load_i import IniContextLoadI
from .calculate_pon_field import CalculatePonField


class TaskMigrationBasedPon:
    def __init__(self, id_to_groups: Dict[int, Group], id_to_robots: Dict[int, Robot],
                 arc_graph: nx.Graph, group_id_to_pfield: Dict[int, PotentialField],
                 robot_id_to_pfield: Dict[int, PotentialField], shortest_path_dict: Dict,
                 id_to_i: Dict[int, float], a: float, b: float):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph
        self.group_id_to_pfield = group_id_to_pfield
        self.robot_id_to_pfield = robot_id_to_pfield
        self.shortest_path_dict = shortest_path_dict
        self.a = a
        self.b = b
        self.id_to_i = id_to_i
        self.records = []

    def run(self) -> List[MigrationRecord]:
        """Execute task migration based on potential field."""
        self._inter_task_migration()
        return self.records

    def _inter_task_migration(self):
        """Inter-group task migration."""
        f_groups = set()
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            if robot.fault_a == 1:
                f_groups.add(robot.group_id)

        average_pe_n = self._get_average_pe_n()

        for fgroup_id in f_groups:
            s_group = self.id_to_groups[fgroup_id]
            robot_id_in_group = s_group.robot_id_in_group

            for robot_id in robot_id_in_group:
                robot = self.id_to_robots[robot_id]
                if robot.fault_a == 1:
                    # pf represents potential field of faulty network layer
                    tnf = list(robot.tasks_list)
                    pf = self.group_id_to_pfield[fgroup_id]
                    p_fg = pf.pegra + pf.perep

                    if p_fg > average_pe_n:
                        # Need inter-layer task migration
                        t_group_id = self._find_min_pn()
                        for task in tnf:
                            pt = self.group_id_to_pfield[t_group_id]
                            p_tg = pt.pegra + pt.perep
                            if p_tg < average_pe_n:
                                self._execute_migration(robot, self.id_to_groups[t_group_id].leader, task)

            # Execute intra-group task migration
            self._intra_task_migration(fgroup_id)

    def _intra_task_migration(self, group_id: int):
        """Intra-group task migration (includes recursive algorithm)."""
        f_robots = []
        group = self.id_to_groups[group_id]

        for robot_id in group.robot_id_in_group:
            robot = self.id_to_robots[robot_id]
            if robot.fault_a == 1:
                f_robots.append(robot)

        leader = group.leader

        # Migrate tasks from faulty robots to prevent cascading failures
        for f_robot in f_robots:
            tasks_list = f_robot.tasks_list
            while len(tasks_list) > 0:
                migrated_task = tasks_list[0]
                migrated_robot = self._find_migrated_robot(f_robot)
                self._execute_migration(f_robot, migrated_robot, migrated_task)
                tasks_list = f_robot.tasks_list

                # Update tasksList
                self._migration_for_robot(migrated_robot)

        self._migration_for_robot(leader)

    def _migration_for_robot(self, robot: Robot):
        """Execute migration for a specific robot."""
        robot_id = robot.robot_id
        neighbors = list(self.arc_graph.neighbors(robot_id))
        domain_id = []

        for neighbor_id in neighbors:
            domain_id.append(neighbor_id)

        domain_id.sort(key=lambda x: self._get_comparator_value(robot, x))

        if not domain_id:
            return

        migrated_id = domain_id[0]

        po_r = self.robot_id_to_pfield[robot_id]
        por_value = po_r.pegra + po_r.perep

        po_m = self.robot_id_to_pfield[migrated_id]
        pom_value = po_m.pegra + po_m.perep

        tasks_list = robot.tasks_list
        migrated_task = self._find_max_task(tasks_list)

        if not self.arc_graph.has_edge(robot_id, migrated_id):
            return

        c = self.arc_graph[robot_id][migrated_id]['weight']

        while ((por_value - pom_value) / c) > 0.02:
            robot_migrated = self.id_to_robots[migrated_id]
            self._execute_migration(robot, robot_migrated, migrated_task)
            self._migration_for_robot(robot_migrated)

            # Continue recursion from ai node
            domain_id.sort(key=lambda x: self._get_comparator_value(robot, x))
            if not domain_id:
                break

            migrated_id = domain_id[0]
            po_r = self.robot_id_to_pfield[robot_id]
            por_value = po_r.pegra + po_r.perep
            po_m = self.robot_id_to_pfield[migrated_id]
            pom_value = po_m.pegra + po_m.perep

    def _get_comparator_value(self, robot: Robot, neighbor_id: int) -> float:
        """Calculate comparison value for sorting neighbors."""
        po1 = self.robot_id_to_pfield[neighbor_id]
        po1_value = po1.pegra + po1.perep

        robot_id = robot.robot_id
        po_m = self.robot_id_to_pfield[robot_id]
        po_m_value = po_m.pegra + po_m.perep

        if not self.arc_graph.has_edge(robot_id, neighbor_id):
            return float('inf')

        cij1 = self.arc_graph[robot_id][neighbor_id]['weight']

        return -((po1_value - po_m_value) / cij1)  # Negate for descending order

    def _find_max_task(self, tasks_list: List[Task]) -> Task:
        """Find task with maximum size."""
        if not tasks_list or len(tasks_list) < 1:
            return None
        return max(tasks_list, key=lambda t: t.size)

    def _find_migrated_robot(self, f_robot: Robot) -> Robot:
        """Find robot to migrate tasks to."""
        migrated_robot = Robot()
        neighbors = list(self.arc_graph.neighbors(f_robot.robot_id))
        min_value = float('inf')

        for neighbor_id in neighbors:
            target_robot = self.id_to_robots[neighbor_id]

            target_p = self.robot_id_to_pfield[target_robot.robot_id]
            weight = self.arc_graph[f_robot.robot_id][neighbor_id]['weight']
            v = (target_p.pegra + target_p.perep) * weight

            if v < min_value:
                migrated_robot = target_robot
                min_value = v

        return migrated_robot

    def _find_min_pn(self) -> int:
        """Find group with minimum potential field."""
        min_value = float('inf')
        return_id = -1

        for group_id in self.group_id_to_pfield.keys():
            p = self.group_id_to_pfield[group_id]
            p_value = p.perep + p.pegra
            if min_value > p_value:
                min_value = p_value
                return_id = group_id

        return return_id

    def _get_average_pe_n(self) -> float:
        """Calculate average potential field of network layer."""
        pe_n_sum = 0.0
        for group_id in self.group_id_to_pfield.keys():
            pe_n = self.group_id_to_pfield[group_id]
            pe_n_sum += pe_n.pegra + pe_n.perep

        return pe_n_sum / len(self.group_id_to_pfield) if self.group_id_to_pfield else 0.0

    def _execute_migration(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Execute task migration from one robot to another."""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        # Update inter-layer load and task list if robots are in different groups
        if robot.group_id != robot_migrated.group_id:
            self._update_inter(robot, robot_migrated, migration_task)

        # Update intra-layer load and task list
        self._update_intra(robot, robot_migrated, migration_task)

        record = MigrationRecord()
        record.from_robot = robot.robot_id
        record.to_robot = robot_migrated.robot_id
        self.records.append(record)

        # Re-initialize contextual load
        ini_context = IniContextLoadI(self.id_to_groups, self.id_to_robots, self.arc_graph,
                                     self.shortest_path_dict, self.id_to_i, self.a, self.b)
        ini_context.run()

        # Update potential field
        calculate_pon_field = CalculatePonField(self.id_to_groups, self.id_to_robots,
                                               self.arc_graph, self.id_to_i,
                                               self.shortest_path_dict, self.a, self.b)

        if robot.group_id != robot_migrated.group_id:
            # Update network layer potential field
            self.group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        # Update node potential field
        self.robot_id_to_pfield = calculate_pon_field.calculate_intra_p()

    def _update_inter(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Update inter-group load and task list."""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        group_id = robot.group_id
        group = self.id_to_groups[group_id]
        robot_migrated_group_id = robot_migrated.group_id
        migrated_group = self.id_to_groups[robot_migrated_group_id]

        group.group_load = group.group_load - migration_task.size
        migrated_group.group_load = migrated_group.group_load + migration_task.size

    def _update_intra(self, robot: Robot, robot_migrated: Robot, migration_task: Task):
        """Update intra-group load and task list after migration."""
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
