import time
import subprocess
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update, union_all

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', 
password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

audit_log = Table('audit_log', metadata, autoload_with=engine)
query = select(audit_log.c.symbol, audit_log.c.time_series_weekly_adjusted).where(audit_log.c.time_series_weekly_adjusted == None)
now = datetime.now()
print("Starting..." + str(now))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    #print("Calling time_series_weekly_adjusted.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 time_series_weekly_adjusted.py " + symbol, shell=True)

then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")

