#!/bin/bash
source /home/env/bin/activate && cd /home/scripts
python3 time_series_nulls.py
deactivate