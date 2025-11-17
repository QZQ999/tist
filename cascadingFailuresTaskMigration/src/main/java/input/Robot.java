package input;

import lombok.Data;

import java.util.List;

@Data
public class Robot {
    private int robotId;
    private double capacity;
    private double  load;
    private List<Task> tasksList;
    private int groupId;
    private double faultA;
    private double faultO;
    private double faultS;
}
