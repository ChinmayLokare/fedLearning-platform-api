#!/bin/bash
set -e # Exit immediately if a command fails.

echo "[WRAPPER-FL-SH] Finding Python executable in virtual environment..."

VENV_PYTHON="/home/ec2-user/app/venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[WRAPPER-FL-ERROR] Python executable not found at $VENV_PYTHON"
    exit 1
fi

echo "[WRAPPER-FL-SH] Executing script with venv's python..."

# Execute the script using the full path to the venv's python interpreter.
"$VENV_PYTHON" src/main/resources/scripts/fl_server.py "$@"

EXIT_CODE=$?
echo "[WRAPPER-FL-SH] Python script finished with exit code: $EXIT_CODE"
exit $EXIT_CODE