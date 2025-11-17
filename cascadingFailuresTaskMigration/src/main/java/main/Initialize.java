package main;

import input.Group;
import input.Robot;
import input.Task;

import java.util.*;

/***
 * 做任务迁移的起始状态下任务和智能体的匹配
 * 在级联故障的场景下，还要做故障情况（过载故障和功能故障、及未来的安全故障的初始化）
 */
public class Initialize {
    Double faultP = 0.5;
    public void run(List<Task> tasks, List<Robot> robots, HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots) {
        iniTask(tasks, robots, idToGroups, idToRobots);
        iniFault(idToRobots,idToGroups);

    }

    private void iniFault(HashMap<Integer, Robot> idToRobots,HashMap<Integer, Group> idToGroups) {
        int size = idToRobots.size();
        int faultSize = (int) (size*faultP);
        if (faultSize==0) {
            faultSize++;
        }
        int step = size/faultSize;
        //0.1表示出现功能故障的节点占据整个系统中节点的比例
        for (int i = 0; i <size ; i++) {
            Robot robot = idToRobots.get(i);
            if (i%step==1) {
                //故障发生这块可以设置成是成片成片的，相邻的节点都发生故障（模拟级联故障的情境）
                robot.setFaultA(1);
                int groupId = robot.getGroupId();
                Group group = idToGroups.get(groupId);
                group.setGroupCapacity(group.getGroupCapacity()-robot.getCapacity());
            }
            Function function = new Function(idToRobots,idToGroups);
            Double faultO = 1-function.calculateOverLoadIS(idToRobots.get(i));
            robot.setFaultO(faultO);
            //设置组件的过载故障概率
        }
    }

    private void iniTask(List<Task> tasks, List<Robot> robots, HashMap<Integer, Group> idToGroups, HashMap<Integer, Robot> idToRobots) {
        //把时刻为-1时的任务分配给各个group及机器人（作为起始状态，只需要考虑对robot的分配即可）
        List<Task> tasksPre = new ArrayList<>();
        for (Task task : tasks) {
            if(task.getArriveTime()!=-1) {
                break;
            }else {
                tasksPre.add(task);
            }
        }
        for (Task task : tasksPre) {
            tasks.remove(task);
            //把已经分配的任务从任务待分配序列中删除
        }
        tasksPre.sort((a, b) -> Double.compare(b.getSize() ,a.getSize()));
        //从大到小排序任务大小，把最大的任务分配给Capacity越大的机器人
        //初始匹配机器人与任务
        PriorityQueue<Robot> pqRobots = new PriorityQueue<>(Comparator.comparingDouble(a -> a.getLoad() / a.getCapacity()));
        robots.sort((a,b)->Double.compare(b.getCapacity(),a.getCapacity()));
        for (Robot robot : robots) {
            //更新group里的机器人（节点编号）
            int groupId = robot.getGroupId();
            Group group = idToGroups.getOrDefault(groupId,new Group());
            Set<Integer> robotIdInGroup = group.getRobotIdInGroup();
            if (robotIdInGroup==null) {
                robotIdInGroup = new HashSet<>();
                robotIdInGroup.add(robot.getRobotId());
            } else {
                robotIdInGroup.add(robot.getRobotId());
            }
            group.setRobotIdInGroup(robotIdInGroup);
            idToGroups.put(groupId,group);

            update(tasksPre,robot,idToGroups);
            pqRobots.offer(robot);
        }
        while (!tasksPre.isEmpty()) {
            //把所有初始的任务匹配完成
            Robot robot = pqRobots.poll();
            update(tasksPre,robot,idToGroups);
            pqRobots.offer(robot);
        }
        //填上group的capacity信息
        for (Integer groupId : idToGroups.keySet()) {
            Group group = idToGroups.get(groupId);
            Set<Integer> robotIdInGroup = group.getRobotIdInGroup();
            Double capacitySum = 0.0;
            for (Integer robotId : robotIdInGroup) {
                capacitySum+=idToRobots.get(robotId).getCapacity();
            }
            group.setGroupCapacity(capacitySum);
        }
    }

    private void update(List<Task> tasksPre, Robot robot, HashMap<Integer, Group> idToGroups) {
        List<Task> robotTasksList = robot.getTasksList();
        if (tasksPre==null||tasksPre.isEmpty()) {
            return;
        }
        robotTasksList.add(tasksPre.get(0));
        //更新机器人的负载情况,把最大的任务交给负载情况最小的机器人
        robot.setLoad(robot.getLoad()+tasksPre.get(0).getSize());
        int groupId = robot.getGroupId();
        //更新group的负载
        Group group = idToGroups.get(groupId);
        group.setGroupLoad(group.getGroupLoad()+tasksPre.get(0).getSize());
        group.setGroupId(groupId);



        tasksPre.remove(0);
        robot.setTasksList(robotTasksList);
    }
}
