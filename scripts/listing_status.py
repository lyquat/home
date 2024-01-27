import random
import fnmatch
from datetime import datetime, date, timedelta
import time
import requests
import subprocess
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update
import csv, urllib.request
import sys
import os
import random

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

inserts = []

def add_to_ignored(symbol):
    ignored = Table('ignored', metadata, autoload_with=engine)
    statement = insert(ignored, {"symbol": symbol})
    result = engine.execute(statement)

def read_remote(path):
    skip_first_line = True
    response = urllib.request.urlopen(url)
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.reader(lines)
    ignored_symbols = ['ZZZ','ZZK','ZXZZT','ZXYZ-A','ZWZZT','ZVZZT','ZVZZC','ZVV','ZTST','ZTEST','ZNTE','ZJZZT','ZBZZT','ZAZZT','ZBZX','USER','IGZ','CTEST','CBX','CBO']
    for row in cr:
        symbol = row[0]
        if skip_first_line:
            skip_first_line = False
            continue
        elif symbol in ignored_symbols:
            continue
        elif symbol.startswith('ATEST') or symbol.startswith('MTEST') or symbol.startswith('NTEST') or symbol.startswith('PTEST'):
            continue
        else:
            status = {
                "symbol": row[0],
                "name": row[1],
                "exchange": row[2],
                "type": row[3],
                "date_listed": row[4],
                "delisted": row[5],
                "status": row[6]
            }
            inserts.append(status)

url = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=demo'
read_remote(url)

listing_status = Table('listing_status', metadata, autoload_with=engine)
statement = delete(listing_status)
result = engine.execute(statement)

statement = insert(listing_status, inserts)
result = engine.execute(statement)

company = Table('company', metadata, autoload_with=engine)
ignored = Table('ignored', metadata, autoload_with=engine)
query = select(listing_status.c.symbol).where(listing_status.c.type == 'Stock').\
where(listing_status.c.symbol.notin_(select(company.c.symbol))).\
where(listing_status.c.symbol.notin_(select(ignored.c.symbol)))

now = datetime.now()
print("Starting..." + str(now))

result = engine.execute(query)
for row in result:
    rand = random.randint(1, 5)
    symbol = row[0]
    print("\tCalling company.py for newly listed symbol:[" + symbol + "]")
    subprocess.call(" python3 company.py " + str(rand) + " " + symbol, shell=True)
    time.sleep(5)
    
then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")
