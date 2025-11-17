#!/usr/bin/env python3
"""
Standalone script to run real-world supply chain case study.
Run from project root: python run_case_study.py
"""
import sys
import os

# Get absolute paths
project_root = os.path.dirname(os.path.abspath(__file__))
python_impl = os.path.join(project_root, "cascadingFailuresTaskMigration_python")
experiments_dir = os.path.join(project_root, "real_world_experiments")

# Change to python implementation directory (this is key!)
os.chdir(python_impl)

# Add paths - add current dir first since we're in python_impl now
sys.path.insert(0, os.getcwd())
sys.path.insert(0, experiments_dir)

# Debug: print sys.path
#print("Current directory:", os.getcwd())
#print("sys.path:", sys.path[:5])

# Now we can import
from experiments.case_study import main

if __name__ == "__main__":
    main()
