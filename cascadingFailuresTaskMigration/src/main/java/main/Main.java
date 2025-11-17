package main;

import LTM.LTM;
import MPFTM.MPFTM;
import input.ExperimentResult;
import input.Reader;
import input.Robot;
import input.Task;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;
import evaluation.EvaluationEtraTarget;

import java.io.IOException;
import java.util.List;

public class Main {
    public static void main(String[] args) throws IOException {
        String tasksFile,graphFile,robotFile;
        tasksFile = "Task24.txt";
        robotFile = "RobotsInformation4.txt";
        graphFile = "Graph4.txt";
        Reader reader = new Reader();

        //测试运行时间
        Double a = 0.1;
        Double b= 1-a;

        List<Task> tasks = reader.readFileToTasks(tasksFile);
        DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph = reader.readFileToGraph(graphFile);
        List<Robot> robots = reader.readFileToRobots(robotFile);
        EvaluationEtraTarget evaluationEtraTarget = new EvaluationEtraTarget();

        Double robotCapacityStd = evaluationEtraTarget.calculateRobotCapacityStd(robots);
        Double taskSizeStd = evaluationEtraTarget.calculateTaskSizeStd(tasks);

        Double meanRobotCapacity = evaluationEtraTarget.calculateMeanRobotCapacity(robots);
        Double meanTaskSize = evaluationEtraTarget.calculateMeanTaskSize(tasks);
        long startTime = System.currentTimeMillis();

        //Tmpf tmpf = new Tmpf(tasks, arcGraph, robots, a, b);
        //ExperimentResult experimentResult = tmpf.tmpfRun();

        //GreedyPath greedyPath = new GreedyPath(tasks, arcGraph, robots, a, b);
        //ExperimentResult experimentResult = greedyPath.greedyRun();

        //Opt opt = new Opt(tasks, arcGraph, robots, a, b);
        //ExperimentResult experimentResult = opt.optRun();
        MPFTM mpftm = new MPFTM(tasks, arcGraph, robots, a, b);
        LTM ltm = new LTM(tasks, arcGraph, robots, a, b);
        ExperimentResult experimentResult = ltm.greedyRun();


        long endTime = System.currentTimeMillis();

        System.out.println("程序运行时间：" + (endTime - startTime) + "ms");
        printExperimentResult(a, b, robotCapacityStd, taskSizeStd, meanRobotCapacity, meanTaskSize, experimentResult);

        System.out.println("*******************************");

        System.out.println("                               ");
        tasks = reader.readFileToTasks(tasksFile);
        startTime = System.currentTimeMillis();
        ExperimentResult experimentResultmpftm = mpftm.mpfmRun();
        endTime = System.currentTimeMillis();
        System.out.println("程序运行时间：" + (endTime - startTime) + "ms");

        printExperimentResult(a, b, robotCapacityStd, taskSizeStd, meanRobotCapacity, meanTaskSize, experimentResultmpftm);
    }

    private static void printExperimentResult(Double a, Double b, Double robotLoadStd, Double taskSizeStd, Double meanRobotCapacity, Double meanTaskSize, ExperimentResult experimentResult) {
        Double meanExecuteCost = experimentResult.getMeanExecuteCost();
        Double meanMigrationCost = experimentResult.getMeanMigrationCost();
        Double meanSurvivalRate = experimentResult.getMeansurvivalRate();

        Double targetOpt = calculateTargetOpt(a,b,meanExecuteCost+meanMigrationCost,meanSurvivalRate);

        System.out.println("meanExecuteCost："+meanExecuteCost);
        System.out.println("meanMigrationCost··："+meanMigrationCost);
        System.out.println("meanSurvivalRate："+meanSurvivalRate);
        System.out.println("robotLoadStd："+robotLoadStd);
        System.out.println("taskSizeStd："+taskSizeStd);
        System.out.println("meanRobotCapacity："+meanRobotCapacity);
        System.out.println("meanTaskSize："+meanTaskSize);
        System.out.println("targetOpt: "+targetOpt);
    }

    private static Double calculateTargetOpt(double a, double b, Double meanCost, Double meanSurvivalRate) {
        return a*meanCost-b*meanSurvivalRate;
    }

}
