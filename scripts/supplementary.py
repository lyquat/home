import time
import subprocess
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update, union_all

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', 
password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

company = Table('company', metadata, autoload_with=engine)
company_supplementary = Table('company_supplementary', metadata, autoload_with=engine)
query = select(company.c.symbol).where(company.c.symbol.notin_(select(company_supplementary.c.symbol)))
#query1 = select(audit_log.c.symbol, audit_log.c.time_series_weekly_adjusted).where(audit_log.c.time_series_weekly_adjusted == None).limit(5)
#query2 = select(audit_log.c.symbol, audit_log.c.time_series_weekly_adjusted).where(audit_log.c.time_series_weekly_adjusted != None).order_by(audit_log.c.time_series_weekly_adjusted)

#query = union_all(query1, query2)
now = datetime.now()
print("Starting..." + str(now))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    print("Calling company_supplementary.py with symbol:[" + symbol + "]")
    subprocess.call(" python3 company_supplementary.py " + symbol, shell=True)

now = datetime.now()
print("Done..." + str(now))
