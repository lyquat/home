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

hundred_days = datetime.now() - timedelta(days=100)
balance_sheet = Table('balance_sheet', metadata, autoload_with=engine)
audit_log = Table('audit_log', metadata, autoload_with=engine)

query = select(balance_sheet.c.symbol, func.max(balance_sheet.c.fiscalDateEnding), audit_log.c.balance_sheet).\
where(balance_sheet.c.symbol == audit_log.c.symbol).\
where(audit_log.c.symbol != None).\
group_by(balance_sheet.c.symbol).\
having(func.max(balance_sheet.c.fiscalDateEnding) <= hundred_days).\
order_by(audit_log.c.balance_sheet, func.max(balance_sheet.c.fiscalDateEnding)).\
limit(50)

now = datetime.now()
print("Starting..." + str(now))

result = engine.execute(query)
for row in result:
    symbol = row[0]
    subprocess.call(" python3 populate_financials.py " + symbol, shell=True)
    
then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")