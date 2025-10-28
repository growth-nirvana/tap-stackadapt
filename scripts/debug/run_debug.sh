#!/bin/bash
# Quick start script for the debug tool

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the debug tool with all arguments passed through
python debug_old_stream_issue.py "$@"

