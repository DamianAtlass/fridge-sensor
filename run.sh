#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# navigate to current directory
cd "${SCRIPT_DIR}/"
. .venv/bin/activate
python main.py
