package MPFTM;

import input.Group;
import input.PotentialField;
import input.Robot;
import main.Function;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.HashMap;
import java.util.Set;

public class CalculatePonField {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer,Robot> idToRobots;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    Double a;
    Double b;
    private HashMap<Integer,Double> idToI ;
    final Double y = 0.005;
    final Double yn = 0.3;
    final Double xn = 0.1;
    final Double x = 0.01;

    public CalculatePonField(HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots, DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph,
                             HashMap<Integer,Double> idToI ,ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, Double a, Double b) {
        this.idToGroups = idToGroups;
        this.idToRobots = idToRobots;
        this.arcGraph = arcGraph;
        this.shortestPath = shortestPath;
        this.a = a;
        this.b = b;
        this.idToI = idToI;
    }

    public HashMap<Integer, PotentialField> calculateIntraP() {
        //计算组件的势场
        HashMap<Integer,PotentialField> IntraPotential = new HashMap<>();
        Double Isum = 0.0;


        for (Integer id : idToRobots.keySet()) {
            Isum+= idToI.get(id);
        }
        Double Imean = Isum/idToRobots.size();
        for (Integer id : idToRobots.keySet()) {
            Robot robot = idToRobots.get(id);
            PotentialField p = new PotentialField();
            //如何设置p
            //设置引力势场，可以加一个对(I-Imean)
            Double I = idToI.get(id);
            p.setPegra(-a*gain(I-Imean));

            //设置斥力势场
            Double ro = 0.0;
            //节点的相邻边
            Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(id);
            for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
                Robot targetRobot = idToRobots.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
                if (targetRobot.getRobotId()==id) {
                    targetRobot = idToRobots.get(arcGraph.getEdgeSource(defaultWeightedEdge));
                }
                if (targetRobot.getGroupId()!=robot.getGroupId()) {
                    continue;
                }
                if (targetRobot.getFaultA()==1) {
                    //到故障节点的距离成反比
                    ro+=1/arcGraph.getEdgeWeight(defaultWeightedEdge);
                }
            }
            if (robot.getFaultA()==1) {
                p.setPerep(Double.MAX_VALUE/2);
            } else if(ro!=0){
                p.setPerep(b*(y*1/ro)*(1/ro));
            } else {
                p.setPerep(0.0);
            }
            IntraPotential.put(id,p);

            //更新过载故障情况
            Function function = new Function(idToRobots,idToGroups);
            Double faultO = 1-function.calculateOverLoadIS(idToRobots.get(id));
            robot.setFaultO(faultO);

        }



        return IntraPotential;
    }

    public HashMap<Integer, PotentialField> calculateInterP() {
        //计算网络层的势场
        HashMap<Integer, PotentialField> InterPotential = new HashMap<>();
        for (Integer groupId : idToGroups.keySet()) {
            Group group = idToGroups.get(groupId);
            PotentialField p = new PotentialField();
            //计算网络层的引力势场（向势场势场降低的方向传递）
            p.setPegra(a*xn*(group.getGroupLoad()));
            //计算网络层中的斥力场
            int fk = 0;
            Set<Integer> robotIdInGroup = group.getRobotIdInGroup();
            for (Integer id : robotIdInGroup) {
                //计算group中的故障节点
                Robot robot = idToRobots.get(id);
                if (robot.getFaultA()==1) {
                    fk+=1;
                }
            }
            int nk = robotIdInGroup.size();
            if (fk== nk) {
                p.setPerep(Double.MAX_VALUE/2);
            } else {
                p.setPerep(b*(yn*(double)fk/(nk-fk)));
            }
            InterPotential.put(groupId,p);
        }

        return InterPotential;
    }

    private Double gain(double x) {

       //return (Math.exp(Math.log(x+1))-Math.exp(-Math.log(x+1)))/(Math.exp(Math.log(x+1))+Math.exp(-Math.log(x+1)));
        return x;
    }
}
