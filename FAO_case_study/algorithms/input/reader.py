import networkx as nx
from typing import List, Dict
from .task import Task
from .robot import Robot


class Reader:
    def read_file_to_graph(self, graph_file: str) -> nx.Graph:
        """Read graph from file and return a NetworkX weighted undirected graph."""
        arc_graph = nx.Graph()

        with open(graph_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                a = int(parts[0])
                b = int(parts[1])
                c = float(parts[2])

                arc_graph.add_node(a)
                arc_graph.add_node(b)
                arc_graph.add_edge(a, b, weight=c)

        return arc_graph

    def read_file_to_tasks(self, tasks_file: str) -> List[Task]:
        """Read tasks from file and return a list of Task objects."""
        tasks = []

        with open(tasks_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()

                # Skip header line (task count) - has only 1 element
                if len(parts) == 1:
                    continue

                task = Task(
                    task_id=int(parts[0]),
                    size=float(parts[1]),
                    arrive_time=int(parts[2])
                )
                tasks.append(task)

        return tasks

    def read_file_to_robots(self, robots_file: str) -> List[Robot]:
        """Read robots from file and return a list of Robot objects."""
        robots = []

        with open(robots_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                robot = Robot(
                    robot_id=int(parts[0]),
                    capacity=float(parts[1]),
                    load=0.0,
                    tasks_list=[],
                    group_id=int(parts[2])
                )
                robots.append(robot)

        return robots
