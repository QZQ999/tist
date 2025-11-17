package MPFTM;

import input.Group;
import input.Robot;
import org.jgrapht.alg.scoring.BetweennessCentrality;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.List;
import java.util.Set;

public class AdLeadersReplace {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    public AdLeadersReplace(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph) {
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        this.arcGraph = arcGraph;
    }
    public void run() {
        for (Integer groupId : idToGroups.keySet()) {
            Group group = idToGroups.get(groupId);
            if (group.getLeader().getFaultA()==1) {
                replace(group);
            }
        }
    }

    private void replace(Group group) {
        List<Robot> adLeaders = group.getAdLeaders();
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
        //这里的I是衡量介数中心性的I
        Robot replaceLeader = adLeaders.get(0);
        Double maxIscore = -1.0;
        for (Robot adLeader : adLeaders) {
            Double Iscore =  (betweennessCentrality.getVertexScore(adLeader.getRobotId())+1)/(1-(1-adLeader.getFaultA())*(1-adLeader.getFaultO()));
            if (Iscore>maxIscore) {
                replaceLeader = adLeader;
                maxIscore = Iscore;
            }
        }
        group.setLeader(replaceLeader);
        adLeaders.remove(replaceLeader);
        group.setAdLeaders(adLeaders);
    }
}
