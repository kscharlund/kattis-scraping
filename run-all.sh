#!/bin/bash
source ~/venv/kattisscraping/bin/activate
cd $(dirname $0)
python fetch_problems.py
python sample_problems.py
python send_to_slack.py
if [ -d /home/www/maxflow.org ]; then
    python write_to_html.py $(date "+%Y-%m-%d") > /home/www/maxflow.org/potw.html
fi
