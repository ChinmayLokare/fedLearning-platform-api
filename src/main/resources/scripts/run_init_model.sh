#!/bin/bash
# This is the Linux version of the wrapper script.
# It assumes it's being run from the project root directory set by Docker.

echo "[WRAPPER-SH] Executing python script with arguments: $@"

# In the Docker container, 'python' will point to our venv's python.
python /app/scripts/init_model.py "$@"

EXIT_CODE=$?
echo "[WRAPPER-SH] Python script finished with exit code: $EXIT_CODE"
exit $EXIT_CODE