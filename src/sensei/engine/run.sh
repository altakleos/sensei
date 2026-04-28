#!/bin/sh
# Sensei script runner — resolves the Python interpreter that has sensei-tutor installed.
# Written by `sensei init`; refreshed by `sensei upgrade`.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH_FILE="$SCRIPT_DIR/.python_path"
export PYTHONPATH="$SCRIPT_DIR/scripts${PYTHONPATH:+:$PYTHONPATH}"

# --- Script-name allowlist (files with __main__ guards) ---
SCRIPT="$1"
case "$SCRIPT" in
  calibration_tracker.py|check_goal.py|check_hints.py|\
  check_profile.py|check_session_notes.py|\
  classify_confidence.py|decay.py|frontier.py|\
  global_knowledge.py|goal_priority.py|hint_decay.py|\
  mastery_check.py|migrate.py|mutate_graph.py|\
  pacing.py|question_density.py|resume_planner.py|\
  review_scheduler.py|session_allocator.py|silence_ratio.py|\
  teaching_density.py) ;;
  *) echo "ERROR: unknown script: $SCRIPT" >&2; exit 1 ;;
esac
shift

if [ -f "$PYTHON_PATH_FILE" ]; then
    PYTHON=$(cat "$PYTHON_PATH_FILE")
    # .python_path must contain an absolute path.
    case "$PYTHON" in
      /*) ;;
      *) echo "ERROR: .python_path must be an absolute path, got: $PYTHON" >&2; exit 1 ;;
    esac
    if [ -x "$PYTHON" ]; then
        exec "$PYTHON" "$SCRIPT_DIR/scripts/$SCRIPT" "$@"
    fi
fi

# Fallback: bare python3
exec python3 "$SCRIPT_DIR/scripts/$SCRIPT" "$@"
