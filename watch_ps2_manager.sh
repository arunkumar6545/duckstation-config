#!/bin/bash
# Auto-commits ps2_manager.py to git whenever the file is saved.
REPO=~/duckstation-config
FILE=$REPO/ps2_manager.py
SOURCE=~/ps2_manager.py

fswatch -o "$SOURCE" | while read; do
  cp "$SOURCE" "$FILE"
  cd "$REPO"
  git add ps2_manager.py
  MSG="Auto-update ps2_manager.py $(date '+%Y-%m-%d %H:%M:%S')"
  git diff --cached --quiet || git commit -m "$MSG" && git push
  echo "[$(date '+%H:%M:%S')] Committed: $MSG"
done
