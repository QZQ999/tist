package input;

import lombok.Data;

@Data
public class ExperimentResult {
    private Double meanMigrationCost;
    private Double meanExecuteCost;
    private Double meansurvivalRate;
}
