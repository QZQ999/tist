package MPFTM;

import input.*;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.*;

public class TaskMigrationBasedPon {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    private HashMap<Integer,PotentialField> groupIdToPfield;
    private HashMap<Integer,PotentialField> robotIdToPfield;
    private List<MigrationRecord> records;
    Double a;
    Double b;
    private HashMap<Integer,Double> idToI;
    public TaskMigrationBasedPon(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots,
                                 DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, HashMap<Integer, PotentialField> groupIdToPfield, HashMap<Integer, PotentialField> robotIdToPfield
            ,ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath,HashMap<Integer,Double> idToI,Double a,Double b) {
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        this.groupIdToPfield = groupIdToPfield;
        this.robotIdToPfield = robotIdToPfield;
        this.arcGraph = arcGraph;
        this.a = a;
        this.b = b;
        this.idToI = idToI;
        this.shortestPath = shortestPath ;
        records = new ArrayList<>();
    }

    public List<MigrationRecord> run() {
        InterTaskMigration();
        return records;
    }

    private void InterTaskMigration() {
        Set<Integer> Fgroups = new HashSet<>();
        for (Integer id : idToRobots.keySet()) {
            Robot robot = idToRobots.get(id);
            if (robot.getFaultA()==1) {
                Fgroups.add(robot.getGroupId());
            }
        }

        Double averagePeN = getAveragePeN();

        for (Integer fgroupId : Fgroups) {
            Group sGroup = idToGroups.get(fgroupId);
            Set<Integer> robotIdInGroup = sGroup.getRobotIdInGroup();
            for (Integer robotId : robotIdInGroup) {
                Robot robot = idToRobots.get(robotId);
                if (robot.getFaultA()==1) {
                    //pf表示发生故障的网络层的势场情况
                    List<Task> tnf = new ArrayList<>(robot.getTasksList());
                    PotentialField pf = groupIdToPfield.get(fgroupId);
                    Double pFg = pf.getPegra()+pf.getPerep();
                    if (pFg >averagePeN) {
                        //需要进行网络层间的任务迁移
                        int tGroupId = findMinPn();
                        for (Task task : tnf) {
                            PotentialField pt = groupIdToPfield.get(tGroupId);
                            Double pTg = pt.getPegra()+pt.getPerep();
                            if (pTg <averagePeN) {
                                excuteMigration(robot,idToGroups.get(tGroupId).getLeader(),task);
                            }
                        }
                    }

                }
            }
            //执行网络层内的任务迁移，对该group内部的任务进行迁移
            IntraTaskMigration(fgroupId);
        }
    }

    private void IntraTaskMigration(int groupId) {
        //执行网络层内的任务迁移，对该group内部的任务进行迁移（包含递归算法）
        List<Robot> fRobots = new ArrayList<>();
        Group group = idToGroups.get(groupId);
        for (Integer robotId : group.getRobotIdInGroup()) {
            Robot robot = idToRobots.get(robotId);
            if (robot.getFaultA()==1) {
                fRobots.add(robot);
            }
        }
        Robot leader = group.getLeader();
        //把需要的被迁移的任务 迁移给边缘的节点上，阻碍级联故障的发生（不设置这种情况了）
        for (Robot fRobot : fRobots) {
            List<Task> tasksList = fRobot.getTasksList();
            while (tasksList.size()>0) {
                Task migratedTask = tasksList.get(0);
                Robot migratedRobot = findMigratedRobot(fRobot);
                excuteMigration(fRobot,migratedRobot,migratedTask);
                tasksList = fRobot.getTasksList();

                //更新tasksList
                MigrationforRobot(migratedRobot);
            }
        }
        MigrationforRobot(leader);

    }

    private void MigrationforRobot(Robot robot) {
        int robotId = robot.getRobotId();
        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(robotId);
        List<Integer> domainId = new ArrayList<>();
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Integer edgeSource = arcGraph.getEdgeSource(defaultWeightedEdge);
            if (edgeSource!=robotId) {
                domainId.add(edgeSource);
            } else {
                Integer edgeTarget = arcGraph.getEdgeTarget(defaultWeightedEdge);
                domainId.add(edgeTarget);
            }
        }
        domainId.sort(getComparator(robot));

        Integer migratedId = domainId.get(0);

        PotentialField poR = robotIdToPfield.get(robotId);

        Double porValue = poR.getPegra()+poR.getPerep();

        PotentialField poM = robotIdToPfield.get(migratedId);

        Double pomValue = poM.getPegra()+poM.getPerep();

        List<Task> tasksList = robot.getTasksList();

        Task migratedTask = findMaxTask(tasksList);

        double c = arcGraph.getEdgeWeight(arcGraph.getEdge(robotId, migratedId));
        while (((porValue-pomValue)/c)>0.02) {
            Robot robotMigrated = idToRobots.get(migratedId);
            excuteMigration(robot, robotMigrated,migratedTask);
            MigrationforRobot(robotMigrated);
            //执行递归

            //从ai节点继续执行递归
            domainId.sort(getComparator(robot));
            migratedId = domainId.get(0);
            poR = robotIdToPfield.get(robotId);
            porValue = poR.getPegra()+poR.getPerep();
            poM = robotIdToPfield.get(migratedId);
            pomValue = poM.getPegra()+poM.getPerep();
        }

    }

    private Task findMaxTask(List<Task> tasksList) {
        if (tasksList==null||tasksList.size()<1) {
            return null;
        }
        Task returnTask = tasksList.get(0);
        for (Task task : tasksList) {
            if (task.getSize()>returnTask.getSize()) {
                returnTask = task;
            }
        }
        return returnTask;
    }

    private Comparator<Integer> getComparator(Robot robot) {
        return new Comparator<Integer>() {
                          @Override
                          public int compare(Integer o1, Integer o2) {
                              PotentialField po1 = robotIdToPfield.get(o1);
                              Double po1Value = po1.getPegra()+po1.getPerep();

                              PotentialField po2 = robotIdToPfield.get(o2);
                              Double po2Value = po2.getPegra()+po2.getPerep();

                              int robotId = robot.getRobotId();
                              PotentialField poM = robotIdToPfield.get(robotId);
                              Double poMValue = poM.getPegra()+poM.getPerep();

                              Double cij1 = arcGraph.getEdgeWeight(arcGraph.getEdge(robotId,o1));

                              Double cij2 = arcGraph.getEdgeWeight(arcGraph.getEdge(robotId,o2));

                              return (int) Math.ceil((po2Value-poMValue)/cij2 - (po1Value-poMValue)/cij1 );
                          }
                      };
    }

    private Robot findMigratedRobot(Robot fRobot) {
        Robot MigratedRobot = new Robot();
        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(fRobot.getRobotId());
        Double minValue = Double.MAX_VALUE;
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Robot targetRobot = idToRobots.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
            if (targetRobot.getRobotId()==fRobot.getRobotId()) {
                targetRobot = idToRobots.get(arcGraph.getEdgeSource(defaultWeightedEdge));
            }
            PotentialField targetP = robotIdToPfield.get(targetRobot.getRobotId());
            Double v = (targetP.getPegra()+targetP.getPerep())*arcGraph.getEdgeWeight(defaultWeightedEdge);
            if (v <minValue) {
                MigratedRobot = targetRobot;
                minValue = v;
            }
        }
        return MigratedRobot;
    }

    private int findMinPn() {
        Double minValue = Double.MAX_VALUE;
        int returnId = -1;
        for (Integer groupId : groupIdToPfield.keySet()) {
            PotentialField p = groupIdToPfield.get(groupId);
            double pValue = p.getPerep() + p.getPegra();
            if (minValue> pValue) {
                minValue = pValue;
                returnId = groupId;
            }
        }
        return returnId;
    }


    private Double getAveragePeN() {
        Double peNsum = 0.0;
        for (Integer groupId : groupIdToPfield.keySet()) {
            PotentialField peN = groupIdToPfield.get(groupId);
            peNsum+= peN.getPegra();
            peNsum+=peN.getPerep();
        }
       return peNsum/groupIdToPfield.size();
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
        //初始化（计算）上下文负载
        new IniContextLoadI(idToGroups,idToRobots,arcGraph, shortestPath,idToI,a, b).run();

        //更新势场情况
        CalculatePonField calculatePonField = new CalculatePonField(idToGroups, idToRobots, arcGraph,idToI,shortestPath,a,b);

        if (robot.getGroupId()!=robotMigrated.getGroupId()) {
            //更新网络层的势场
            groupIdToPfield = calculatePonField.calculateInterP();

        }

        //更新节点的势场
        robotIdToPfield = calculatePonField.calculateIntraP();

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
