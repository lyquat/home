import subprocess
import random
import csv
import sys
import os
import requests
import fnmatch
import mysql.connector
from datetime import datetime, date, timedelta
import time

symbol = ''
args = sys.argv
if len(args) == 2:
    symbol = args[1]
    rand = random.randint(1, 5)
    print("\ttime_series_weekly_adjusted1.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 time_series_weekly_adjusted1.py " + str(rand) + " " + symbol, shell=True)
    time.sleep(5)
else:
    exit("ERROR: No symbol supplied")


