package input;

import lombok.Data;

import java.util.List;
import java.util.Set;

@Data
public class Group {
    private int groupId;
    private double groupLoad;
    private Robot leader;
    private Set<Integer> robotIdInGroup;
    private List<Task> assignedTasks;
    private double groupCapacity;
    private List<Robot> adLeaders;
}
