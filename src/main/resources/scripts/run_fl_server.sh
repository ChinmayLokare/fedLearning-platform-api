#!/bin/bash
echo "[WRAPPER-FL-SH] Executing python script with arguments: $@"
python /app/scripts/fl_server.py "$@"
EXIT_CODE=$?
echo "[WRAPPER-FL-SH] Python script finished with exit code: $EXIT_CODE"
exit $EXIT_CODE