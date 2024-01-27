#!/bin/bash
source /home/env/bin/activate && cd /home/lyquat
python3 freeze_snapshot.py
cp -r /home/build/* /home/public_html/
rm -rf /home/build/*