package main;

import input.Group;
import input.Robot;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.Set;

public class Function {
    HashMap<Integer, Robot> idToRobots;
    HashMap<Integer, Group> idToGroups;

    public Function(HashMap<Integer, Robot> idToRobots, HashMap<Integer, Group> idToGroups) {
        this.idToRobots = idToRobots;
        this.idToGroups = idToGroups;
    }

    public Double calculateOverLoadIS(Robot robot){
        //计算Individual Survivability
        double load = robot.getLoad();
        //获取组的生存评分
        double GS = calculateGS(idToGroups.get(robot.getGroupId()));
        //这里的存活率函数要好好设置一下
        return Math.max(GS*(1-sig(load/60)),0.3);

    }

    private Double calculateGS(Group group) {
        //计算Group Survivability
        double groupLoad = group.getGroupLoad();
        //用类似sigmod函数的变体做0-1之间的单调非增函数
        int size = group.getRobotIdInGroup().size();
        return Math.max(1-sig(groupLoad/(size*200)),0.6);
        //用来函数内进行调用
    }


    private Double sig(double x) {
        return (Math.exp(Math.log(x+1))-Math.exp(-Math.log(x+1)))/
                (Math.exp(Math.log(x+1))+Math.exp(-Math.log(x+1)));
    }

    public Double calculateContextualLoad(Robot leader, Robot robot,
                                          DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,
                                          ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath,
                                          Double a , Double b) {
        double f = a*robot.getLoad()/robot.getCapacity()-b* calculateOverLoadIS(robot);
        //由相连边获取了domainF
        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(robot.getRobotId());
        double domianF = 0;
        double costSum = 0;
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Robot targetRobot = idToRobots.get(arcGraph.getEdgeTarget(defaultWeightedEdge));

            if (targetRobot.getGroupId()!=robot.getGroupId()||targetRobot.getRobotId()==robot.getRobotId()) {
                continue;
            }
            //与其相连边的沟通成本之和
            costSum+=arcGraph.getEdgeWeight(defaultWeightedEdge);
            domianF+=a*targetRobot.getLoad()/targetRobot.getCapacity()-b* calculateOverLoadIS(targetRobot);
        }
        int size = defaultWeightedEdges.size()+1;
        int domainNum = size +1;

        //加上进行层间任务迁移的cost
        double pathWeight = shortestPath.getPathWeight(leader.getRobotId(), robot.getRobotId());
        costSum+= pathWeight;
        //负载这个函数得想想
        return f+0.1*(domianF/domainNum+costSum/ size);
    }

}
