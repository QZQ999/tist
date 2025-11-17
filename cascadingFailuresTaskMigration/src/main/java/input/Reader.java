package input;

import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Reader {
    public DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> readFileToGraph(String graphFile) throws IOException {
        BufferedReader bufferedReader;
        String cur[];
        bufferedReader = new BufferedReader(new FileReader(graphFile));
        String line = null;
        //用JGraph定义一个无向的权重图
        DefaultUndirectedWeightedGraph<Integer,DefaultWeightedEdge> arcGraph =
                new DefaultUndirectedWeightedGraph<>(DefaultWeightedEdge.class);
        int a, b;
        double c ;
        while ((line = bufferedReader.readLine()) != null) {
            cur = line.split(" ");
            //1.向图中添加点
            a = Integer.parseInt(cur[0]);
            b = Integer.parseInt(cur[1]);
            c = Integer.parseInt(cur[2]);
            arcGraph.addVertex(a);
            arcGraph.addVertex(b);

            //2.向图中添加边

            DefaultWeightedEdge defaultWeightedEdge = arcGraph.addEdge(a,b);
            arcGraph.setEdgeWeight(defaultWeightedEdge,c);
        }

        return arcGraph ;
    }
    public List<Task> readFileToTasks(String tasksFile) throws IOException {
        BufferedReader bufferedReader;
        String cur[];
        bufferedReader = new BufferedReader(new FileReader(tasksFile));
        String line = null;
        List<Task> tasks = new ArrayList<>();
        while ((line = bufferedReader.readLine()) != null) {
            cur = line.split(" ");
            Task task = new Task();
            task.setTaskId(Integer.parseInt(cur[0]));
            task.setSize(Integer.parseInt(cur[1]));
            task.setArriveTime(Integer.parseInt(cur[2]));
            tasks.add(task);
        }
        //用一个三元组来刻画tasks，TaskId(task[0])表示第i个任务的编号,Size(task[1])表示任务的大小，
        // ArriveTime(task[3])表示任务的到来时间
        return tasks;
    }

    public List<Robot> readFileToRobots(String tasksFile) throws IOException {
        BufferedReader bufferedReader;
        String cur[];
        bufferedReader = new BufferedReader(new FileReader(tasksFile));
        String line = null;
        List<Robot> robots = new ArrayList<>();
        while ((line = bufferedReader.readLine()) != null) {
            cur = line.split(" ");
            Robot robot = new Robot();
            robot.setRobotId(Integer.parseInt(cur[0]));
            robot.setCapacity(Integer.parseInt(cur[1]));
            robot.setLoad(0);
            robot.setTasksList(new ArrayList<>());
            robot.setGroupId(Integer.parseInt(cur[2]));
            robots.add(robot);
        }
        //用一个三元组来刻画robots，robot[0]表示机器人编号，robot[1]表示机器人能力，
        //robot[2]表示机器人所在group的编号
        return robots;
    }
}
