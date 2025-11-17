package MPFTM;

import input.Group;
import input.Robot;
import main.Function;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;

public class IniContextLoadI {
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    Double a;
    Double b;
    private HashMap<Integer,Double> idToI ;
    public IniContextLoadI(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots,
                           DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath,
                           HashMap<Integer, Double> idToI, Double a, Double b) {
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        this.arcGraph = arcGraph;
        this.a = a;
        this.b = b;
        this.idToI = idToI;
        this.shortestPath = shortestPath;
    }

    public void run() {
        Function function = new Function(idToRobots,idToGroups);
        for (Integer id : idToRobots.keySet()) {
            Robot robot = idToRobots.get(id);
            Group group = idToGroups.get(robot.getGroupId());
            Double I = function.calculateContextualLoad(group.getLeader(), robot, arcGraph, shortestPath, a, b);
            if (I>1000||I<-1000) {
                I = 1.0;
            }
            idToI.put(id,I);
        }
    }
}
