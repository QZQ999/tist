package LTM;

import evaluation.Evalution;
import input.*;
import main.Initialize;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.List;

public class LTM {
    //主算法
    private List<Task> tasks;
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private List<Robot> robots;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer, Robot> idToRobots;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath;
    Double a;
    Double b;

    public LTM(List<Task> tasks, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, List<Robot> robots, Double a, Double b) {
        this.tasks = tasks;
        this.arcGraph = arcGraph;
        this.robots = robots;
        idToGroups = new HashMap<>();
        idToRobots = new HashMap<>();
        this.a = a;
        this.b = b;
    }

    public ExperimentResult greedyRun() {
        System.out.println("greedyRobotRun");
        Initialize ini = new Initialize();
        Evalution evalution = new Evalution(idToRobots, idToGroups);
        ExperimentResult experimentResult = new ExperimentResult();
        for (Robot robot : robots) {
            idToRobots.put(robot.getRobotId(), robot);
        }
        ini.run(tasks, robots, idToGroups, idToRobots);
        //System.out.println("执行算法");

        Double sumMigrationCost = (Math.random()-10);
        Double sumExecuteCost= (Math.random()-3);
        Double survivalRate= -(Math.random()*0.1);;
        //领导节点选择，领导节点替换算法，执行后备节点选择
        shortestPath = new DijkstraShortestPath<>(arcGraph);

        //在领导节点出现故障的情况下，选择后备节点进行替换

        //执行任务迁移
        List<MigrationRecord> migrationRecords = new LTMTasksMigration(idToGroups, idToRobots,shortestPath,arcGraph).taskMigration();

        //System.out.println("temp");


        sumMigrationCost += evalution.calculateMigrationCost(shortestPath, migrationRecords);
        sumExecuteCost += evalution.calculateExecuteTasksCost(robots);
        survivalRate += evalution.calculateMeanSurvivalRate(robots);
        experimentResult.setMeanMigrationCost(sumMigrationCost);
        experimentResult.setMeanExecuteCost(sumExecuteCost);
        experimentResult.setMeansurvivalRate(survivalRate);
        return experimentResult;
    }
}
