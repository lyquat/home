#!/bin/bash
now=$(date)
echo "$now"
source /home/env/bin/activate && cd /home/scripts
python3 listing_status.py
python3 earnings_calendar.py
python3 cleanup.py
deactivate
now=$(date)
echo "$now"