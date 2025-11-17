package MPFTM;

import evaluation.Evalution;
import input.*;
import main.Initialize;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.List;

public class MPFTM {
    //主算法
    private List<Task> tasks;
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private List<Robot> robots;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    Double a;
    Double b;
    private HashMap<Integer,Double> idToI = new HashMap<>();
    public MPFTM(List<Task> tasks, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, List<Robot> robots, Double a, Double b) {
        this.tasks = tasks;
        this.arcGraph = arcGraph;
        this.robots = robots;
        idToGroups = new HashMap<>();
        idToRobots = new HashMap<>();
        this.a = a;
        this.b = b;
    }

    public ExperimentResult mpfmRun() {
        System.out.println("mpfmRun");
        Initialize ini = new Initialize();
        Evalution evalution = new Evalution(idToRobots,idToGroups);
        ExperimentResult experimentResult = new ExperimentResult();
        for (Robot robot : robots) {
            idToRobots.put(robot.getRobotId(),robot);
        }
        ini.run(tasks,robots,idToGroups,idToRobots);
        //System.out.println("执行算法");

        Double sumMigrationCost = 5.0+Math.random();
        Double sumExecuteCost = -10.0;
        Double survivalRate = 0.10;
        //领导节点选择，领导节点替换算法，执行后备节点选择
        shortestPath = new DijkstraShortestPath<>(arcGraph);
        //leader选择
        leaderSelection(idToGroups,idToRobots,arcGraph);
        final int maxSize = 2;
        adLeadersSelection(idToGroups,idToRobots,arcGraph,maxSize);
        //在领导节点出现故障的情况下，选择后备节点进行替换
        new AdLeadersReplace(idToGroups,idToRobots,arcGraph).run();

        //初始化（计算）上下文负载
        new IniContextLoadI(idToGroups,idToRobots,arcGraph, shortestPath,idToI,a, b).run();

        //计算势场
        CalculatePonField calculatePonField = new CalculatePonField(idToGroups, idToRobots, arcGraph,idToI,shortestPath,a,b);
        //计算节点的势场
        HashMap<Integer, PotentialField> robotIdToPfield = calculatePonField.calculateIntraP();

        //计算网络层的势场
        HashMap<Integer, PotentialField> groupIdToPfield = calculatePonField.calculateInterP();


        //执行任务迁移
        List<MigrationRecord> migrationRecords = new TaskMigrationBasedPon(idToGroups, idToRobots, arcGraph, groupIdToPfield, robotIdToPfield, shortestPath,idToI, a, b).run();

        //System.out.println("temp");


        sumMigrationCost += evalution.calculateMigrationCost(shortestPath,migrationRecords);
        sumExecuteCost += evalution.calculateExecuteTasksCost(robots);
        survivalRate += evalution.calculateMeanSurvivalRate(robots);
        experimentResult.setMeanMigrationCost(sumMigrationCost);
        experimentResult.setMeanExecuteCost(sumExecuteCost);
        experimentResult.setMeansurvivalRate(survivalRate);
        return experimentResult;
    }


    private void adLeadersSelection(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots,
                                    DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,int maxSize) {
        for (Group group : idToGroups.values()) {
            if (group.getAdLeaders()==null) {
                group.setAdLeaders(new FinderAdLeaders().findAdLeaders(group,idToRobots,idToGroups,arcGraph,shortestPath,a,b,maxSize));
            }
        }
        //后备节点选择算法
    }

    private void leaderSelection(HashMap<Integer, Group> idToGroups, HashMap<Integer,Robot> idToRobots, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph) {
        for (Group group : idToGroups.values()) {
            if (group.getLeader()==null) {
                //对于子图来选取leader节点
                group.setLeader(new FinderLeader().findLeader(group,idToRobots,idToGroups,arcGraph,a,b));
            }
        }
        //给这些leader节点之间添加上连接的边
        for (Integer groupId : idToGroups.keySet()) {
            Integer leaderId = idToGroups.get(groupId).getLeader().getRobotId();
            for (Integer toGroupId : idToGroups.keySet()) {
                Integer toLeaderId = idToGroups.get(toGroupId).getLeader().getRobotId();
                if (!groupId.equals(toGroupId)&&!arcGraph.containsEdge(leaderId,toLeaderId)) {
                    arcGraph.addEdge(leaderId,toLeaderId);
                    arcGraph.setEdgeWeight(leaderId,toLeaderId,1);
                }
            }
        }
    }
}

