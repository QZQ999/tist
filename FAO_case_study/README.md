# FAO Food Trade Network Case Study

**Standalone Package for Real-World Algorithm Validation**

Complete, self-contained experimental package for validating task migration algorithms on authentic international food trade network data from FAO (Food and Agriculture Organization of the United Nations).

## 📦 Package Contents

```
FAO_case_study/
├── algorithms/              # All algorithm implementations
│   ├── input/              # Data structures (Task, Robot, Group, etc.)
│   ├── LTM/                # CATM algorithm
│   ├── MPFTM/              # HCTM-MPF algorithm
│   ├── greedyPath/         # KBTM algorithm
│   ├── evaluation/         # Performance evaluation
│   └── main/               # Initialization utilities
├── data/                   # FAO data and loader
│   ├── FAO_Multiplex_Trade/  # Original FAO dataset
│   │   └── Dataset/
│   │       ├── fao_trade_nodes.txt        # 214 countries
│   │       ├── fao_trade_layers.txt       # 364 food products
│   │       └── fao_trade_multiplex.edges  # 318,346 trade connections
│   └── fao_data_loader.py  # Data loading and preprocessing
├── visualization/          # Academic figure generation
│   └── academic_plots.py   # Publication-quality plots
├── results/               # Output directory (auto-created)
│   ├── figures/           # PDF and PNG figures
│   ├── tables/            # Results tables (TXT and JSON)
│   └── data/              # Generated network files
├── run_case_study.py      # ⭐ ONE-CLICK RUNNER
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Installation

```bash
# Navigate to the package directory
cd FAO_case_study

# Install dependencies
pip install -r requirements.txt
```

### One-Click Execution

```bash
# Run the complete case study
python run_case_study.py
```

That's it! The script will:
1. Load FAO data (214 countries, 364 food products)
2. Select top 10 products by trade volume
3. Build aggregated trade network
4. Generate realistic tasks based on trade patterns
5. Run benchmark algorithms (CATM, KBTM)
6. Generate academic figures (5 publication-quality plots)
7. Save all results

## 📊 Generated Outputs

### 1. Academic Figures (`results/figures/`)

**All figures generated in both PDF and PNG formats**:

- **`performance_comparison.pdf/png`** - 4-panel performance comparison
  - (a) Task Survival Rate
  - (b) Total Migration Cost
  - (c) Cost Breakdown (stacked bar)
  - (d) Computational Efficiency

- **`network_topology.pdf/png`** - Network visualization
  - Node size ∝ country capacity
  - Node color = capacity group
  - Sample of top 100 countries by capacity

- **`capacity_distribution.pdf/png`** - Capacity analysis
  - (a) Histogram with statistics
  - (b) Box plot with outliers

- **`performance_radar.pdf/png`** - Multi-dimensional comparison
  - 5 metrics: Survival Rate, Cost Efficiency, Speed, Robustness, Scalability
  - Radar chart showing algorithm profiles

- **`improvement_analysis.pdf/png`** - Improvement over random baseline
  - Shows +88-98% improvement
  - Clear comparison to 50% random baseline

### 2. Results Tables (`results/tables/`)

- **`results.txt`** - Human-readable table
- **`results.json`** - Machine-readable JSON format

### 3. Network Data Files (`results/data/`)

- **`FAO_Trade_Graph.txt`** - Network topology
- **`FAO_Trade_Robots.txt`** - Country/agent configurations
- **`FAO_Trade_Tasks.txt`** - Generated tasks

## 📈 Expected Results

### Algorithm Performance (Default Configuration)

| Algorithm | Survival Rate | Total Cost | Runtime |
|-----------|---------------|------------|---------|
| CATM (LTM) | **94.33%** | -12.52 | ~630ms |
| KBTM (GreedyPath) | **99.21%** | 0.00 | ~770ms |

### Key Findings

- ✅ **Exceptional survival rates**: >94% on real-world network
- ✅ **High improvement**: +88-98% over random baseline (50%)
- ✅ **Computational efficiency**: Sub-second execution for 210-node network
- ✅ **Cost-effective**: Negative/zero migration costs
- ✅ **Practical validation**: Works on authentic international trade data

## 🔧 Customization

### Modify Experimental Parameters

Edit `run_case_study.py` at the bottom:

```python
results = run_experiment(
    top_k=10,      # Number of top products to select (1-364)
    num_tasks=50,  # Number of tasks to generate
    a=0.1,         # Cost weight in objective function
    b=0.9,         # Survival rate weight in objective function
    seed=42        # Random seed for reproducibility
)
```

### Run Specific Components

```python
# Import modules
from data.fao_data_loader import FAODataLoader
from visualization.academic_plots import AcademicPlotter

# Load FAO data
loader = FAODataLoader(data_dir='data/FAO_Multiplex_Trade/Dataset')

# Select products
top_layers = loader.select_top_layers(top_k=10, by='total_weight')

# Build network
G, capacities = loader.build_aggregated_network(selected_layers=top_layers)

# Generate visualizations
plotter = AcademicPlotter(output_dir='results/figures')
plotter.plot_network_topology(G, capacities)
```

## 📚 Dataset Information

### FAO Multiplex Trade Network

- **Source**: Food and Agriculture Organization of the United Nations (FAO)
- **Year**: 2010
- **Scale**: 214 countries, 364 food products, 318,346 trade connections
- **Type**: Directed, weighted, multilayer network

**Reference**:
> De Domenico, M., Nicosia, V., Arenas, A., & Latora, V. (2015).
> Structural reducibility of multilayer networks.
> *Nature Communications*, 6(1), 6864.
> DOI: [10.1038/ncomms7864](https://doi.org/10.1038/ncomms7864)

### Top 10 Products (by trade volume)

1. Soybeans - 69,221,746 (136 countries)
2. Food preparations (nes) - 44,372,878 (196 countries)
3. Crude materials - 35,947,995 (207 countries)
4. Wine - 29,299,734 (171 countries)
5. Palm oil - 28,715,901 (155 countries)
6. Wheat - 27,173,417 (152 countries)
7. Natural rubber - 25,659,021 (136 countries)
8. Maize - 23,768,824 (154 countries)
9. Distilled alcoholic beverages - 23,602,617 (172 countries)
10. Beef and veal - 23,345,546 (148 countries)

## 🎯 Use Cases

### For Research Papers

1. **Run the experiment**: `python run_case_study.py`
2. **Use the figures**: All figures in `results/figures/` are publication-ready
3. **Cite the results**: Use data from `results/tables/results.txt`
4. **Reference the dataset**: See citation above

### For Algorithm Development

- Test new algorithms on the same real-world network
- Compare against CATM and KBTM baselines
- Use consistent experimental setup for fair comparison

### For Network Analysis

- Analyze real international trade patterns
- Study multi-layer network properties
- Visualize global trade relationships

## 🔬 Technical Details

### Network Construction

1. **Layer Selection**: Top K products by total trade volume
2. **Aggregation**: Sum trade volumes across selected products
3. **Node Filtering**: Remove isolated nodes (no trade connections)
4. **ID Remapping**: Convert FAO node IDs (1-214) to algorithm IDs (0-based)

### Capacity Calculation

Countries are assigned capacities based on total trade volume using logarithmic scaling:

```
capacity = 10 + 190 * (log(volume + 1) - log(min_volume + 1)) /
                       (log(max_volume + 1) - log(min_volume + 1))
```

Result: Capacity range [10, 200], mean ~125, std ~42

### Task Generation

Tasks represent trade orders/shipments:
- Sampled from trade routes proportional to their volume
- Task size ∝ trade volume (with randomness)
- Arrival times uniformly distributed

### Edge Weights

Represent transportation cost/distance:
```
distance = max(1.0, 1000 / (trade_volume + 1))
```

Higher trade volume → shorter effective distance (established trade routes)

## 📖 Algorithm Details

### CATM (Context-Aware Task Migration)

- Greedy algorithm based on local context awareness
- Considers neighboring nodes' states
- O(N*M) time complexity

### KBTM (Key-Based Task Migration)

- Identifies key nodes using centrality measures
- Utilizes shortest path algorithms
- Higher computational cost but better performance

## 🐛 Troubleshooting

### Import Errors

Ensure you're running from the `FAO_case_study/` directory:
```bash
cd FAO_case_study
python run_case_study.py
```

### Missing Dependencies

Install requirements:
```bash
pip install -r requirements.txt
```

For visualization:
```bash
pip install matplotlib numpy
```

### Matplotlib Backend Issues

If you see display errors:
```python
# Add at top of run_case_study.py
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

## 📝 Output Interpretation

### Survival Rate

Percentage of tasks successfully migrated:
- **>90%**: Excellent
- **80-90%**: Good
- **<80%**: Needs improvement

### Total Cost

Sum of execution and migration costs:
- **Negative**: Migration actually reduces cost (优化效果)
- **Zero**: Perfect load balancing
- **Positive**: Added overhead (but may still be worthwhile if survival rate high)

### Runtime

Computational time in milliseconds:
- **<1000ms**: Excellent for real-time applications
- **1-5s**: Good for periodic optimization
- **>5s**: May need optimization for large-scale deployment

## 🌟 Features

- ✅ **Completely standalone**: All code and data in one package
- ✅ **One-click execution**: Single command to run everything
- ✅ **Publication-ready figures**: High-quality PDF and PNG outputs
- ✅ **Real-world data**: Authentic FAO international trade network
- ✅ **Reproducible**: Fixed random seeds and documented parameters
- ✅ **Extensible**: Easy to add new algorithms or modify parameters
- ✅ **Well-documented**: Comprehensive README and code comments

## 📧 Support

For questions about:
- **Dataset**: See FAO website or De Domenico et al. paper
- **Algorithms**: Check algorithm source code in `algorithms/`
- **Visualization**: See `visualization/academic_plots.py`

## 📄 License

- **Algorithms**: Provided as-is for research purposes
- **FAO Dataset**: Open Database License (ODbL) - see `data/FAO_Multiplex_Trade/LICENSE_*.txt`

## 🙏 Acknowledgments

- FAO (Food and Agriculture Organization) for the trade network data
- De Domenico et al. for dataset preparation and initial analysis
- NetworkX developers for graph algorithms library

---

**Ready to validate your algorithms on real-world data!** 🚀

Just run: `python run_case_study.py`
