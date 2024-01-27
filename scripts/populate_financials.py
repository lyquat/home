import sys
import subprocess
import time

def call_scripts():
    print("\tCalling cashflow.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 cashflow.py " + symbol, shell=True)
    time.sleep(10)
    print("\tCalling income_statement.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 income_statement.py " + symbol, shell=True)
    time.sleep(10)
    print("\tCalling balance_sheet.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 balance_sheet.py " + symbol, shell=True)
    time.sleep(10)
    print("")

symbol = None
args = sys.argv
if len(args) != 2:
    exit("ERROR: No symbol supplied")
else:
    symbol = args[1]
    call_scripts()
