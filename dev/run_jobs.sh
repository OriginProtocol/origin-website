#!/bin/bash
###############################
## For use in docker containers
###############################

echo "$(date +%H:%M:%S) | Running jobs..."

PWD="$(pwd)"
export PYTHONPATH="/app:$PYTHONPATH"

cd /app

python3 /app/logic/scripts/fetch_github_stats.py
python3 /app/logic/scripts/fetch_social_stats.py
python3 /app/logic/scripts/send_welcome_drips.py
python3 /app/logic/scripts/update_token_insight.py

cd $PWD

echo "$(date +%H:%M:%S) | Jobs complete."
