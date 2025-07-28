#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "[WRAPPER-SH] Activating Python virtual environment..."

# Define the path to the activation script
VENV_ACTIVATE="/home/ec2-user/app/venv/bin/activate"

# Check if the activation script exists
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "[WRAPPER-ERROR] Virtual environment not found at /home/ec2-user/app/venv"
    exit 1
fi

# Activate the virtual environment
source "$VENV_ACTIVATE"

echo "[WRAPPER-SH] Environment activated. Executing init_model.py..."

# Execute the python script, passing along all arguments ("$@").
# We can use a relative path because the Java ProcessBuilder sets the working directory.
python3 src/main/resources/scripts/init_model.py "$@"

EXIT_CODE=$?
echo "[WRAPPER-SH] Python script finished with exit code: $EXIT_CODE"

# Deactivation happens automatically when the script exits
exit $EXIT_CODE