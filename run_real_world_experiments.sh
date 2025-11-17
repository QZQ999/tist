#!/bin/bash
#
# Wrapper script to run real-world experiments
# This ensures the correct working directory and Python path setup
#

cd "$(dirname "$0")"

export PYTHONPATH="$(pwd)/cascadingFailuresTaskMigration_python:$(pwd)/real_world_experiments:$PYTHONPATH"

python3 real_world_experiments/run_experiments.py "$@"
