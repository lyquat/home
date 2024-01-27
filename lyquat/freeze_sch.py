import subprocess
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy import asc, desc
from sqlalchemy import cast, Numeric
from sqlalchemy.sql import select, text
from datetime import datetime
import time

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

audit_log = Table('audit_log', metadata, autoload_with=engine)
query = select(audit_log.c.symbol, audit_log.c.time_series_weekly_adjusted).\
order_by(audit_log.c.time_series_weekly_adjusted, audit_log.c.symbol)

now = datetime.now()
print("Starting..." + str(now))
result = engine.execute(query)
for row in result:
	symbol = row[0]
	print("\tfreezing symbol:[" + symbol + "]")
	subprocess.call("python3 freeze_symbol.py " + symbol, shell=True)
	time.sleep(10)

then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")