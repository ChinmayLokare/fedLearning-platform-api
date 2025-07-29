#!/bin/bash
set -e # Exit immediately if a command fails.

echo "[WRAPPER-SH] Finding Python executable in virtual environment..."

# Define the absolute path to the python executable inside the venv
VENV_PYTHON="/home/ec2-user/app/venv/bin/python"

# Check if the python executable exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "[WRAPPER-ERROR] Python executable not found at $VENV_PYTHON"
    exit 1
fi

echo "[WRAPPER-SH] Executing script with venv's python..."

# --- THIS IS THE FIX ---
# Execute the script using the full path to the venv's python interpreter.
# We no longer need to run 'source' or 'activate'.
"$VENV_PYTHON" src/main/resources/scripts/init_model.py "$@"

EXIT_CODE=$?
echo "[WRAPPER-SH] Python script finished with exit code: $EXIT_CODE"
exit $EXIT_CODE