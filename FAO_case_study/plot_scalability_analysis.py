#!/usr/bin/env python3
"""
Plot scalability analysis from saved data
Allows flexible customization of plotting style and appearance
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# ========== CUSTOMIZABLE PLOT SETTINGS ==========
# You can adjust these parameters to change the plot appearance

# Figure settings
FIGURE_WIDTH = 12
FIGURE_HEIGHT = 4
DPI = 300

# Line and marker settings
LINE_WIDTH = 2.5
MARKER_SIZE = 8
CAPSIZE = 4  # Error bar cap size
CAPTHICK = 2  # Error bar cap thickness

# Color scheme (Wong 2011 colorblind-friendly palette)
COLORS = {
    'CATM': '#E69F00',      # Orange
    'KBTM': '#56B4E9',      # Sky Blue
    'HCTM-MPF': '#009E73',  # Bluish Green
}

MARKERS = {
    'CATM': 'o',
    'KBTM': 's',
    'HCTM-MPF': '^',
}

# Font settings
FONT_SIZE = 10
AXIS_LABEL_SIZE = 11
TITLE_SIZE = 12
LEGEND_SIZE = 9

# Grid settings
GRID_ALPHA = 0.3
GRID_STYLE = '--'

# Error bar settings
ERROR_BAR_ALPHA = 0.6  # Transparency of error bars


def load_data():
    """Load scalability data from JSON file"""
    data_file = os.path.join(current_dir, 'results', 'data', 'scalability_data.json')

    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        print("Please run: python generate_scalability_data.py first")
        return None

    with open(data_file, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded scalability data from: {data_file}")
    return data


def create_scalability_plot():
    """Create professional scalability analysis figure"""

    # Load data
    data = load_data()
    if data is None:
        return

    task_loads = np.array(data['task_loads'])
    algorithms = data['algorithms']

    # Set publication-quality defaults
    rcParams['figure.dpi'] = DPI
    rcParams['savefig.dpi'] = DPI
    rcParams['font.family'] = 'serif'
    rcParams['font.size'] = FONT_SIZE
    rcParams['axes.labelsize'] = AXIS_LABEL_SIZE
    rcParams['axes.titlesize'] = TITLE_SIZE
    rcParams['legend.fontsize'] = LEGEND_SIZE
    rcParams['lines.linewidth'] = LINE_WIDTH

    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

    # ========== Panel (a): Task Survival Rate ==========
    for alg_name in ['CATM', 'KBTM', 'HCTM-MPF']:
        alg_data = algorithms[alg_name]
        mean = np.array(alg_data['survival_mean'])
        std = np.array(alg_data['survival_std'])

        ax1.errorbar(task_loads, mean, yerr=std,
                    label=alg_name, color=COLORS[alg_name], marker=MARKERS[alg_name],
                    markersize=MARKER_SIZE, capsize=CAPSIZE, capthick=CAPTHICK,
                    alpha=1.0, elinewidth=LINE_WIDTH, markeredgewidth=1.5)

    ax1.set_xlabel('Number of Tasks', fontweight='bold')
    ax1.set_ylabel('Task Survival Rate (%)', fontweight='bold')
    ax1.set_title('(a) Task Survival Rate', fontweight='bold', pad=10)
    ax1.grid(True, alpha=GRID_ALPHA, linestyle=GRID_STYLE)
    ax1.legend(loc='best', frameon=True, framealpha=0.9)
    ax1.set_ylim([85, 105])
    ax1.set_xticks(task_loads)

    # ========== Panel (b): Normalized System Cost ==========
    for alg_name in ['CATM', 'KBTM', 'HCTM-MPF']:
        alg_data = algorithms[alg_name]
        mean = np.array(alg_data['cost_mean'])
        std = np.array(alg_data['cost_std'])

        ax2.errorbar(task_loads, mean, yerr=std,
                    label=alg_name, color=COLORS[alg_name], marker=MARKERS[alg_name],
                    markersize=MARKER_SIZE, capsize=CAPSIZE, capthick=CAPTHICK,
                    alpha=1.0, elinewidth=LINE_WIDTH, markeredgewidth=1.5)

    ax2.set_xlabel('Number of Tasks', fontweight='bold')
    ax2.set_ylabel('Normalized System Cost', fontweight='bold')
    ax2.set_title('(b) Normalized System Cost', fontweight='bold', pad=10)
    ax2.grid(True, alpha=GRID_ALPHA, linestyle=GRID_STYLE)
    ax2.legend(loc='best', frameon=True, framealpha=0.9)
    ax2.set_xticks(task_loads)

    # ========== Panel (c): Runtime ==========
    for alg_name in ['CATM', 'KBTM', 'HCTM-MPF']:
        alg_data = algorithms[alg_name]
        mean = np.array(alg_data['runtime_mean'])
        std = np.array(alg_data['runtime_std'])

        ax3.errorbar(task_loads, mean, yerr=std,
                    label=alg_name, color=COLORS[alg_name], marker=MARKERS[alg_name],
                    markersize=MARKER_SIZE, capsize=CAPSIZE, capthick=CAPTHICK,
                    alpha=1.0, elinewidth=LINE_WIDTH, markeredgewidth=1.5)

    ax3.set_xlabel('Number of Tasks', fontweight='bold')
    ax3.set_ylabel('Runtime (seconds)', fontweight='bold')
    ax3.set_title('(c) Runtime', fontweight='bold', pad=10)
    ax3.grid(True, alpha=GRID_ALPHA, linestyle=GRID_STYLE)
    ax3.legend(loc='best', frameon=True, framealpha=0.9)
    ax3.set_xticks(task_loads)

    plt.tight_layout()

    # Save figure
    output_dir = os.path.join(current_dir, 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, 'scalability_analysis.pdf')
    png_path = os.path.join(output_dir, 'scalability_analysis.png')

    plt.savefig(pdf_path, bbox_inches='tight', dpi=DPI)
    plt.savefig(png_path, bbox_inches='tight', dpi=DPI)
    plt.close()

    print(f"\n✓ Scalability plots saved:")
    print(f"  {pdf_path}")
    print(f"  {png_path}")
    print(f"\nTo customize plot appearance:")
    print(f"  1. Edit plot_scalability_analysis.py")
    print(f"  2. Modify settings at the top (FIGURE_WIDTH, LINE_WIDTH, COLORS, etc.)")
    print(f"  3. Run: python plot_scalability_analysis.py")


def print_statistics():
    """Print statistical summary of scalability data"""
    data = load_data()
    if data is None:
        return

    print("\n" + "="*80)
    print("SCALABILITY DATA SUMMARY")
    print("="*80)

    task_loads = data['task_loads']
    print(f"\nTask loads: {task_loads}")

    for alg_name in ['CATM', 'KBTM', 'HCTM-MPF']:
        print(f"\n{alg_name}:")
        alg_data = data['algorithms'][alg_name]

        print(f"  Survival rate: {alg_data['survival_mean']}")
        print(f"  Survival std:  {alg_data['survival_std']}")
        print(f"  Cost mean:     {alg_data['cost_mean']}")
        print(f"  Cost std:      {alg_data['cost_std']}")
        print(f"  Runtime mean:  {alg_data['runtime_mean']}")
        print(f"  Runtime std:   {alg_data['runtime_std']}")

    print("="*80)


if __name__ == "__main__":
    create_scalability_plot()
    print_statistics()
