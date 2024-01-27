import requests
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', 
password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

def build(symbol, e, e_data):
    week = datetime.fromisoformat(e)
    data = json_data

    open_p = e_data["1. open"]
    high_p = e_data["2. high"]
    low_p = e_data["3. low"]
    close_p = e_data["4. close"]
    adj_close_p = e_data["5. adjusted close"]
    volume = e_data["6. volume"]
    div_amount = e_data["7. dividend amount"]

    insert = {"symbol": symbol, "week_ending": week, "open": open_p, "high": high_p, "low": low_p, "close": close_p, "adjusted_close": adj_close_p, "volume": volume}
    return insert

route = None
symbol = None

args = sys.argv
if len(args) == 3:
    route = args[1]
    symbol = args[2]
else:
    exit("ERROR: No symbol or route supplied in " + sys.argv[0])

url = 'XXXXX.amazonaws.com/' + str(route) + '?symbol=' + symbol
response = requests.get(url, timeout=20)
json_data = response.json() if response and response.status_code == 200 else None

if json_data and 'Weekly Adjusted Time Series' in json_data:
    time_series = json_data['Weekly Adjusted Time Series']

    inserts = []

    for e in time_series:
        today = datetime.today()
        week = datetime.fromisoformat(e)
        delta = today - timedelta(weeks= 53 * 10)
        if week < delta:
            continue
        else:
            foo = json_data['Weekly Adjusted Time Series'][e]
            tsw_data = build(symbol, e, foo)
            inserts.append(tsw_data)

    time_series_weekly_adjusted = Table('time_series_weekly_adjusted', metadata, autoload_with=engine)
    statement = delete(time_series_weekly_adjusted).where(time_series_weekly_adjusted.c.symbol == symbol)
    engine.execute(statement)
    ins = time_series_weekly_adjusted.insert()
    engine.execute(ins, inserts)
else:
    print("unexpected data:\r")
    print(json_data)