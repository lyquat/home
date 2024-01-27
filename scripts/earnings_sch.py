import os
import fnmatch
import csv
import random
import time
import subprocess
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update, func, desc, union_all

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

#diff = date.today() - timedelta(days=40)

#earnings_view = Table('earnings_view', metadata, autoload_with=engine)
#query = select(earnings_view.c.symbol).\
#group_by(earnings_view.c.symbol).\
#having(func.datediff(func.max(earnings_view.c.forecast_report_date),func.max(earnings_view.c.reportedDate))>40).\
#order_by(desc(func.datediff(func.max(earnings_view.c.forecast_report_date),func.max(earnings_view.c.reportedDate))), earnings_view.c.symbol).\
#limit(300)

audit_log = Table('audit_log', metadata, autoload_with=engine)
query = select(audit_log.c.symbol, audit_log.c.earnings).where(audit_log.c.earnings != None).order_by(audit_log.c.earnings).limit(100)

result = engine.execute(query)
now = datetime.now()
print("Starting..." + str(now))
for row in result:
    symbol = row[0]
    rand = random.randint(1, 5)
    print("\tearnings.py with symbol:[" + symbol + "]")
    subprocess.call("python3 earnings.py " + str(rand) + " " + symbol, shell=True)
    time.sleep(5)
        
then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")

