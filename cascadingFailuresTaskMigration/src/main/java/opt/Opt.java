package opt;

import evaluation.Evalution;
import input.*;
import main.Initialize;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;
import MPFTM.FinderLeader;

import java.util.HashMap;
import java.util.List;

public class Opt {
    //主算法
    private List<Task> tasks;
    private List<Robot> robots;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    Double a;
    Double b;
    public Opt(List<Task> tasks, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,
               List<Robot> robots, Double a, Double b) {
        this.tasks = tasks;
        this.robots = robots;
        this.arcGraph = arcGraph;
        idToGroups = new HashMap<>();
        idToRobots = new HashMap<>();
        this.a = a;
        this.b = b;
    }

    public ExperimentResult optRun() {
        System.out.println("optRun");
        Initialize ini = new Initialize();
        Evalution evalution = new Evalution(idToRobots, idToGroups);
        ExperimentResult experimentResult = new ExperimentResult();
        for (Robot robot : robots) {
            idToRobots.put(robot.getRobotId(), robot);
        }
        ini.run(tasks, robots, idToGroups, idToRobots);
        leaderSelection(idToGroups,idToRobots,arcGraph);

        Double sumExecuteCost;
        Double survivalRate;
        Double sumMigrationCost;

        shortestPath = new DijkstraShortestPath<>(arcGraph);
        List<MigrationRecord> migrationRecords = new OptMigration(shortestPath,idToGroups,idToRobots,a,b).run();
        //搞一个最优分配的方式
        sumMigrationCost = evalution.calculateMigrationCost(shortestPath, migrationRecords);
        sumExecuteCost = evalution.calculateExecuteTasksCost(robots);
        survivalRate = evalution.calculateMeanSurvivalRate(robots);

        experimentResult.setMeanExecuteCost(sumExecuteCost);
        experimentResult.setMeansurvivalRate(survivalRate);
        experimentResult.setMeanMigrationCost(sumMigrationCost);
        return experimentResult;
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
                    arcGraph.setEdgeWeight(leaderId,toLeaderId,10);
                }
            }
        }
    }
}
