package MPFTM;

import input.Group;
import input.Robot;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.alg.scoring.BetweennessCentrality;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.*;

public class FinderAdLeaders {
    public List<Robot> findAdLeaders(Group group, HashMap<Integer, Robot> idToRobots, HashMap<Integer, Group> idToGroups,
                                     DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,
                                     ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, Double a, Double b, int maxSize) {
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

        //选择后备节点,后备节点按ref大小进入优先队列进行排序
        //I=b/(1-(1-FA)(1-FO))
        //ref = b*d
        Map<Integer,Double> idToRefmap = new HashMap<>();
        for (Integer id : robotIdSet) {
            Robot robot = idToRobots.get(id);
            if (robot.getFaultA() == 1) {
                idToRefmap.put(id,Double.MIN_VALUE);
                //表示此时已经发生了功能故障，后备适应性的值处于最小状态
            } else {
                //betweennessCentrality+1，让最短路径包括从自己到自己，每个节点的阶数中心性的值最小为1
                Double Iscore =  (betweennessCentrality.getVertexScore(id)+1)/(1-(1-robot.getFaultA())*(1-robot.getFaultO()));
                Double d;
                if(shortestPath.getPath(group.getLeader().getRobotId(),robot.getRobotId())==null) {
                    d = 100000.0;
                } else {
                    d = shortestPath.getPathWeight(group.getLeader().getRobotId(),robot.getRobotId());
                }
                idToRefmap.put(id,Iscore*d);
            }
        }

        PriorityQueue<Robot> adLeadersPq= new PriorityQueue<>((o1,o2)->
                (int) Math.ceil(idToRefmap.get(o1.getRobotId())
                                        -idToRefmap.get(o2.getRobotId())));
        //适应性从小向大排列

        for (Integer id : robotIdSet) {
            //选择ref最大的几个节点加入到优先队列中并返回
            if (adLeadersPq.size()<maxSize) {
                adLeadersPq.offer(idToRobots.get(id));
            } else {
                double minRef = idToRefmap.get(adLeadersPq.peek().getRobotId());
                if (idToRefmap.get(id)>minRef) {
                    adLeadersPq.poll();
                    adLeadersPq.offer(idToRobots.get(id));
                }
            }
        }
        return new ArrayList<>(adLeadersPq);
    }
}
