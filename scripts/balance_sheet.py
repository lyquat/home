import subprocess
import random
import csv
import sys
import os
import requests
import fnmatch
import mysql.connector
from datetime import datetime, date, timedelta

def getRandomKey():
    path = 'api_keys2.txt'
    keys = []
    key = ''
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            keys.append(row)      
        file.close()
        key = random.choice(keys)[0]
    return key

key = getRandomKey()
symbol = ''
args = sys.argv
if len(args) == 2:
    symbol = args[1]
    subprocess.call(" python3 balance_sheet1.py " + key + " " + symbol, shell=True)
else:
    exit("ERROR: No symbol supplied")


