import requests
import time
import json
from sqlalchemy import create_engine, MetaData, Table, select, func, bindparam, Interval, desc, insert

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

company = Table('company', metadata, autoload_with=engine)
wayback = Table('wayback', metadata, autoload_with=engine)
industry = Table('industry', metadata, autoload_with=engine)

query = select(industry.c.industryid)
result = engine.execute(query)
for row in result:
    try:
        industryid = str(row[0])
        url = "https://web.archive.org/save/Lyquat.com/list/" + industryid
        wb_url = "https://archive.org/wayback/available?url=https://lyquat.com/list/" + industryid
        foo=requests.get(wb_url, timeout=10)
        y = foo.json()
        is_archived = y['archived_snapshots']
        if(len(is_archived) == 0):
            x = requests.get(url, timeout=60)
            print("  " + str(x.status_code) + " - " + url)
            time.sleep(45)
        else:
            #n = {"symbol": industryid, "is_archived": 'Y', "checked": func.now()}
            #statement = insert(wayback).values(n)
            #engine.execute(statement)
            print("\t" + industryid + " already archived ")
    except Exception as e:
        print("Error on industry ID: " + str(id))
        print(e)

        continue
    
print("done")