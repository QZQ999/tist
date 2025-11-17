package evaluation;

import input.Group;
import input.MigrationRecord;
import input.Robot;
import input.Task;
import main.Function;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.List;

public class Evalution {
    HashMap<Integer, Robot> idToRobots;
    HashMap<Integer, Group> idToGroups;
    //计算迁移成本
    Function function;

    public Evalution(HashMap<Integer, Robot> idToRobots, HashMap<Integer, Group> idToGroups) {
        this.idToRobots = idToRobots;
        this.idToGroups = idToGroups;
        function = new Function(idToRobots, idToGroups);
    }

    public Double calculateMigrationCost(ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, List<MigrationRecord> migrationRecords) {
        Double sum = 0.0;
        //计算总的迁移成本
        for (MigrationRecord migrationRecord : migrationRecords) {
            double pathWeight = shortestPath.getPathWeight(migrationRecord.getFrom(), migrationRecord.getTo());
            sum += pathWeight;
        }


        return sum;
    }

    //计算完成任务的成本
    public Double calculateExecuteTasksCost(List<Robot> robots) {
        Double sum = 0.0;
        //Function function = new Function(idToRobots, idToGroups);
        for (Robot robot : robots) {
            List<Task> tasksList = robot.getTasksList();
            if (tasksList != null) {
                for (Task task : tasksList) {
                    sum += task.getSize() / robot.getCapacity();
                }
            }
        }
        return sum;
    }

    //计算平均存活率
    public Double calculateMeanSurvivalRate(List<Robot> robots) {
        Double sum = 0.0;
        int count = 0;
        for (Robot robot : robots) {
            if (robot.getFaultA()!=1) {
                count++;
            }
            Double survivalRate = (1-robot.getFaultA())*(1-robot.getFaultO());
            sum += survivalRate;
        }
        return sum / count;
    }


}
