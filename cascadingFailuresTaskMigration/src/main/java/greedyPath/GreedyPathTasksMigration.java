package greedyPath;

import input.Group;
import input.MigrationRecord;
import input.Robot;
import input.Task;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

public class GreedyPathTasksMigration {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath;
    HashMap<Integer, Group> idToGroups;
    HashMap<Integer, Robot> idToRobots;
    private List<MigrationRecord> records;

    public GreedyPathTasksMigration(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots, ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph) {
        this.arcGraph = arcGraph;
        this.shortestPath = shortestPath;
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        records = new ArrayList<>();
    }

    public List<MigrationRecord> taskMigration() {
        //应该记录哪个任务从哪个机器人迁移到哪，进行return
        for (Integer robotId : idToRobots.keySet()) {
            Robot robot = idToRobots.get(robotId);
            if (robot.getFaultA()==1) {
                List<Task> tfs = new ArrayList<>(robot.getTasksList());
                for (Task task : tfs) {
                    Robot robotMigrated = greedyFindMigratedRobotByPath(robot);
                    excuteMigration(robot,robotMigrated,task);
                }
            }
        }
        return records;
    }

    private Robot greedyFindMigratedRobotByPath(Robot fRobot) {
        Robot migratedRobot = new Robot();
        ShortestPathAlgorithm.SingleSourcePaths<Integer, DefaultWeightedEdge> paths = shortestPath.getPaths(fRobot.getRobotId());

        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(fRobot.getRobotId());
        Double minPathWeight = Double.MAX_VALUE;
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Robot targetRobot = idToRobots.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
            if (targetRobot.getRobotId()==fRobot.getRobotId()) {
                targetRobot = idToRobots.get(arcGraph.getEdgeSource(defaultWeightedEdge));
            }
            if (targetRobot.getGroupId()!=fRobot.getGroupId()) {
                continue;
            }

            double pathWeight = shortestPath.getPathWeight(fRobot.getRobotId(),targetRobot.getRobotId());
            if (pathWeight <minPathWeight && targetRobot.getFaultA()!=1) {
                minPathWeight = pathWeight;
                migratedRobot = targetRobot;
            }

        }
        return migratedRobot;
    }

    private void excuteMigration(Robot robot, Robot robotMigrated,Task migrationTask) {
        if (robot == null) {
            return;
        }

        if (robotMigrated == null) {
            return;
        }
        if (migrationTask == null) {
            return;
        }

        //改变网络层间负载和任务列表
        if (robot.getGroupId()!=robotMigrated.getGroupId()) {
            //不在同一组才会更新网络层间的势场情况
            updateInter(robot, robotMigrated, migrationTask);
        }
        //改变网络层内负载和任务列表
        updateIntra(robot, robotMigrated, migrationTask);
        MigrationRecord record = new MigrationRecord();
        record.setFrom(robot.getRobotId());
        record.setTo(robotMigrated.getRobotId());
        records.add(record);
    }
    private void updateInter(Robot robot, Robot robotMigrated, Task migrationTask) {
        if (robot == null) {
            return;
        }

        if (robotMigrated == null) {
            return;
        }
        if (migrationTask == null) {
            return;
        }

        int groupId = robot.getGroupId();
        Group group = idToGroups.get(groupId);
        int robotMigratedGroupId = robotMigrated.getGroupId();
        Group migratedGroup = idToGroups.get(robotMigratedGroupId);

        group.setGroupLoad(group.getGroupLoad()-migrationTask.getSize());
        migratedGroup.setGroupLoad(migratedGroup.getGroupLoad()+migrationTask.getSize());


    }

    private void updateIntra(Robot robot, Robot robotMigrated, Task migrationTask) {
        //更新迁移后的任务负载
        List<Task> tasksList = robot.getTasksList();
        tasksList.remove(migrationTask);
        robot.setLoad(robot.getLoad()-migrationTask.getSize());
        robot.setTasksList(tasksList);


        List<Task> robotMigratedTaskList = robotMigrated.getTasksList();
        if (robotMigratedTaskList==null) {
            robotMigratedTaskList = new ArrayList<>();
        }

        robotMigratedTaskList.add(migrationTask);
        robotMigrated.setLoad(robotMigrated.getLoad()+migrationTask.getSize());
        robotMigrated.setTasksList(robotMigratedTaskList);

    }
}
