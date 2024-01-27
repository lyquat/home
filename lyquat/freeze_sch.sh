#!/bin/bash
source /home/env/bin/activate && cd /home/lyquat
python3 freeze_sch.py
cp -Rf /home/build/* /home/public_html/
rm -rf /home/build/*