package MPFTM;

import input.Group;
import input.Robot;
import main.Function;
import org.jgrapht.alg.scoring.BetweennessCentrality;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.Set;

public class FinderLeader {
    public Robot findLeader(Group group, HashMap<Integer, Robot> idToRobots, HashMap<Integer, Group> idToGroups,
                            DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,
                            Double a, Double b) {
        DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> subGraph = new DefaultUndirectedWeightedGraph<>(DefaultWeightedEdge.class);
        Set<Integer> robotIdSet = group.getRobotIdInGroup();
        for (Integer robotId : robotIdSet) {
            subGraph.addVertex(robotId);
            Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(robotId);
            for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
                Integer target = subGraph.getEdgeTarget(defaultWeightedEdge);

                if (target.equals(robotId)) {
                    continue;
                }

                if (group.getGroupId()!=idToRobots.get(target).getGroupId()) {
                    continue;
                    //不属于这一层的节点（比如由leader节点与其他lead而节点相连节点），不要加到子图中
                }
                subGraph.addVertex(target);
                //把这一层的节点加入到子图中
                if(!subGraph.containsEdge(robotId,target)){
                    //去掉重复的边,不包含这个边，则加入这个边
                    DefaultWeightedEdge temp = subGraph.addEdge(robotId,target);
                    subGraph.setEdgeWeight(temp,arcGraph.getEdgeWeight(defaultWeightedEdge));
                }
            }
        }
        //计算子图的介数中心性
        BetweennessCentrality<Integer, DefaultWeightedEdge> betweennessCentrality = new BetweennessCentrality<>(subGraph);
        int leaderId = -1;
        double MaxIscore = -1.0;
        for (int i = 0; i <robotIdSet.size() ; i++) {
            for (Integer vertex : robotIdSet) {
                Function function = new Function(idToRobots,idToGroups);
                double bcValue = betweennessCentrality.getVertexScore(vertex);
                double p =function.calculateOverLoadIS(idToRobots.get(vertex));
                double Iscore = a*bcValue*b*p;
                if(Iscore>MaxIscore) {
                    MaxIscore = Iscore;
                    leaderId = vertex;
                }
            }
        }
        return idToRobots.get(leaderId);
    }

}
