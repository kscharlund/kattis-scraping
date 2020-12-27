#!/bin/bash
source ~/venv/kattisscraping/bin/activate
cd $(dirname $0)
python fetch_problems.py
python sample_problems.py
python send_to_slack.py
