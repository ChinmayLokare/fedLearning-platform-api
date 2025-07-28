#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "[WRAPPER-FL-SH] Activating Python virtual environment..."

VENV_ACTIVATE="/home/ec2-user/app/venv/bin/activate"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "[WRAPPER-FL-ERROR] Virtual environment not found at /home/ec2-user/app/venv"
    exit 1
fi

source "$VENV_ACTIVATE"

echo "[WRAPPER-FL-SH] Environment activated. Executing fl_server.py..."

# Call the correct python script
python3 src/main/resources/scripts/fl_server.py "$@"

EXIT_CODE=$?
echo "[WRAPPER-FL-SH] Python script finished with exit code: $EXIT_CODE"

exit $EXIT_CODE