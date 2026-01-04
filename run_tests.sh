#!/bin/bash
# Helper script to run tests with venv activated

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate venv
source "$SCRIPT_DIR/venv/bin/activate"

# Run the real URL test script with arguments
python "$SCRIPT_DIR/test_real_urls.py" "$@"
