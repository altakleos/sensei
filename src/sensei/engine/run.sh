#!/bin/sh
# Sensei script runner — resolves the Python interpreter that has sensei-tutor installed.
# Written by `sensei init`; refreshed by `sensei upgrade`.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH_FILE="$SCRIPT_DIR/.python_path"

if [ -f "$PYTHON_PATH_FILE" ]; then
    PYTHON=$(cat "$PYTHON_PATH_FILE")
    if [ -x "$PYTHON" ]; then
        exec "$PYTHON" "$SCRIPT_DIR/scripts/$@"
    fi
fi

# Fallback: bare python3
exec python3 "$SCRIPT_DIR/scripts/$@"
