import time
import subprocess
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update, func
import csv, urllib.request

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

url = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=demo'

def read_remote(path, inserts):
    skip_first_line = True
    response = urllib.request.urlopen(url)
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.reader(lines)
    for row in cr:
        #print(row)
        if skip_first_line:
            skip_first_line = False
            continue
        else:
            if row[4] == '' or row[4] == '0':
                continue
            estimate = row[4]
            calendar_data = {
                "symbol": row[0],
                "name": row[1],
                "report_date": row[2],
                "fiscal_date_ending": row[3],
                "estimate": estimate,
                "currency": row[5]
            }
            inserts.append(calendar_data)

inserts = []
read_remote(url, inserts)

py_now = datetime.now()

earnings_calendar = Table('earnings_calendar', metadata, autoload_with=engine)
for i in inserts:
    f = "%Y-%m-%d"
    symbol = i["symbol"]
    fde = i["fiscal_date_ending"]
    fiscal_date_ending = datetime.strptime(fde,f)
    q = select(earnings_calendar.c.symbol).\
    where(earnings_calendar.c.symbol == symbol).\
    where(earnings_calendar.c.fiscal_date_ending == fiscal_date_ending)
    rows = engine.execute(q).all()
    count = len(rows)
    if count>0:
        print("Earnings calendar date for symbol [" + symbol + "] exists...updating")
        statement = update(earnings_calendar).\
        where(earnings_calendar.c.symbol == symbol).\
        where(earnings_calendar.c.fiscal_date_ending == fiscal_date_ending).values(i)
        result = engine.execute(statement)
    else:
        print("Earnings date for symbol [" + symbol + "] does *not exist...adding")
        statement = insert(earnings_calendar).values(i)
        result = engine.execute(statement)






