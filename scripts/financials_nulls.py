import sys
import random
import csv
import subprocess
import time
from sqlalchemy import create_engine, MetaData, Table, select, func
from datetime import datetime, timedelta

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

#schedule_financials = Table('schedule_financials', metadata, autoload_with=engine)
#query = select(schedule_financials.c.symbol).\
#where(schedule_financials.c.fiscal_date_ending > schedule_financials.c.max_date).\
#limit(50)
hundred_days = datetime.now() - timedelta(days=100)
balance_sheet = Table('balance_sheet', metadata, autoload_with=engine)
audit_log = Table('audit_log', metadata, autoload_with=engine)

now = datetime.now()
print("Starting..." + str(now))
query = select(audit_log.c.symbol).where(audit_log.c.balance_sheet == None).limit(100)
result = engine.execute(query)
for row in result:
    symbol = row[0]
    subprocess.call(" python3 populate_financials.py " + symbol, shell=True)
    print("\r")
    
then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")