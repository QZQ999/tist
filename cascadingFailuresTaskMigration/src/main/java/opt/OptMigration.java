package opt;

import evaluation.Evalution;
import input.Group;
import input.MigrationRecord;
import input.Robot;
import input.Task;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class OptMigration {
    ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath;
    HashMap<Integer, Group> idToGroups;
    HashMap<Integer, Robot> idToRobots;
    Double a;
    Double b;
    HashMap<Integer,Robot> bestIdRobots ;
    HashMap<Integer,Group> bestIdGroups ;
    Double minTargetValue = Double.MAX_VALUE;
    HashMap<Task,Robot> taskToRobot ;
    List<Task> allTasks = new ArrayList<>();
    public OptMigration(ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath,
                        HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots,
                        Double a, Double b) {
        this.shortestPath = shortestPath;
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        this.a = a;
        this.b = b;
    }

    public List<MigrationRecord> run() {
        for (Integer robotId : idToRobots.keySet()) {
            Robot robot = idToRobots.get(robotId);
            allTasks.addAll(robot.getTasksList());
        }

        HashMap<Integer,Robot> idToRobotsTemp =  robotMapCopyOrg(idToRobots);
        HashMap<Integer, Group> idToGroupsTemp = groupMapCopyOrg(idToGroups);
        taskToRobot = new HashMap<>();

        for (Integer robotId : idToRobots.keySet()) {
            Robot robot = idToRobots.get(robotId);
            List<Task> tasksList = robot.getTasksList();
            for (Task task : tasksList) {
                taskToRobot.put(task,robot);
            }
        }

        bestIdRobots = robotMapCopy(idToRobots);
        bestIdGroups = groupMapCopy(idToGroups);

        backtrace(idToRobotsTemp,idToGroupsTemp,allTasks,0);

        //用计算迁移的函数来返回
        List<MigrationRecord> ret;
        ret = calculateMigrationRecord(bestIdRobots);
        return ret;
    }



    private void backtrace(HashMap<Integer, Robot> idToRobotsTemp, HashMap<Integer, Group> idToGroupsTemp,List<Task> allTasks,int index) {
        if (index==allTasks.size()) {
            Double targetValue = calculateTargetValue(idToRobotsTemp,idToGroupsTemp);
            if (targetValue<minTargetValue) {
                bestIdGroups = groupMapCopy(idToGroupsTemp);
                bestIdRobots = robotMapCopy(idToRobotsTemp);
                minTargetValue = targetValue;
                System.out.println(index+" "+minTargetValue);
            }
            return;
        }
        for (Integer id : idToRobotsTemp.keySet()) {
            Robot robotTemp = idToRobotsTemp.get(id);
            if (robotTemp.getFaultA()==1) {
                continue;
                //有故障的节点不能够接收任务
            }
            for (int i = index;i<allTasks.size();i++) {
                Task task = allTasks.get(i);
                List<Task> tasksList = robotTemp.getTasksList();
                tasksList.add(task);
                robotTemp.setTasksList(tasksList);
                robotTemp.setLoad(robotTemp.getLoad()+task.getSize());
                backtrace(idToRobotsTemp,idToGroupsTemp,allTasks,index+1);
                tasksList.remove(task);
                robotTemp.setLoad(robotTemp.getLoad()-task.getSize());
            }
        }
    }

    private Double calculateTargetValue(HashMap<Integer, Robot> idToRobotsTemp, HashMap<Integer, Group> idToGroupsTemp) {
        List<MigrationRecord> tempMigrationRecords =calculateMigrationRecord(idToRobotsTemp);
        Evalution evalution = new Evalution(idToRobotsTemp,idToGroupsTemp);
        Double survivalRate = evalution.calculateMeanSurvivalRate(new ArrayList<>(idToRobotsTemp.values()));
        Double executeTasksCost = evalution.calculateExecuteTasksCost(new ArrayList<>(idToRobotsTemp.values()));
        Double migrationCost = evalution.calculateMigrationCost(shortestPath, tempMigrationRecords);
        return a*(executeTasksCost+migrationCost)-b*survivalRate;
    }

    private List<MigrationRecord> calculateMigrationRecord(HashMap<Integer, Robot> idToRobotsTemp) {
        List<MigrationRecord> records = new ArrayList<>();
        for (Integer id : idToRobots.keySet()) {
            Robot robotTemp = idToRobotsTemp.get(id);
            for (Task task : robotTemp.getTasksList()) {
                if (taskToRobot.keySet().contains(task)) {
                    Robot robot = taskToRobot.get(task);
                    if(robot.getRobotId()!=id) {
                        MigrationRecord record = new MigrationRecord();
                        record.setFrom(robot.getRobotId());
                        record.setTo(id);
                        records.add(record);
                    }
                }
            }
        }
        return records;
    }


    private HashMap<Integer, Robot> robotMapCopyOrg(HashMap<Integer, Robot> idToRobots) {
        HashMap<Integer,Robot> idToRobotsTemp =  new HashMap<>();
        for (Integer id : idToRobots.keySet()) {
            Robot robot = idToRobots.get(id);
            Robot robotTemp = new Robot();
            robotTemp.setLoad(0);
            robotTemp.setTasksList(new ArrayList<>());
            robotTemp.setGroupId(robot.getGroupId());
            robotTemp.setCapacity(robot.getCapacity());
            robotTemp.setRobotId(id);
            idToRobotsTemp.put(id,robotTemp);
        }
        return idToRobotsTemp;
    }

    private HashMap<Integer, Group> groupMapCopyOrg(HashMap<Integer, Group> idToGroups) {
        HashMap<Integer,Group> idToGroupsTemp = new HashMap<>();
        for (Integer groupId : idToGroups.keySet()) {
            Group group = idToGroups.get(groupId);
            Group groupTemp = new Group();
            groupTemp.setGroupLoad(0);
            groupTemp.setGroupCapacity(group.getGroupCapacity());
            groupTemp.setLeader(group.getLeader());
            groupTemp.setGroupId(groupId);
            groupTemp.setRobotIdInGroup(group.getRobotIdInGroup());
            idToGroupsTemp.put(groupId,groupTemp);
        }
        return idToGroupsTemp;
    }


    private HashMap<Integer, Robot> robotMapCopy(HashMap<Integer, Robot> idToRobots) {
        HashMap<Integer,Robot> idToRobotsTemp =  new HashMap<>();
        for (Integer id : idToRobots.keySet()) {
            Robot robot = idToRobots.get(id);
            Robot robotTemp = new Robot();
            robotTemp.setLoad(robot.getLoad());
            robotTemp.setTasksList(robot.getTasksList());
            robotTemp.setGroupId(robot.getGroupId());
            robotTemp.setCapacity(robot.getCapacity());
            robotTemp.setRobotId(id);
            idToRobotsTemp.put(id,robotTemp);
        }
        return idToRobotsTemp;
    }

    private HashMap<Integer, Group> groupMapCopy(HashMap<Integer, Group> idToGroups) {
        HashMap<Integer,Group> idToGroupsTemp = new HashMap<>();
        for (Integer groupId : idToGroups.keySet()) {
            Group group = idToGroups.get(groupId);

            Group groupTemp = new Group();
            groupTemp.setGroupLoad(group.getGroupLoad());
            groupTemp.setGroupCapacity(group.getGroupCapacity());
            groupTemp.setLeader(group.getLeader());
            groupTemp.setGroupId(groupId);
            groupTemp.setRobotIdInGroup(group.getRobotIdInGroup());
            idToGroupsTemp.put(groupId,groupTemp);
        }
        return idToGroupsTemp;
    }
}
