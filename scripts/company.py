import sys
import os
import csv
import random
import requests
import fnmatch
from datetime import datetime, date
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

route = None
symbol = None

args = sys.argv
if len(args) == 3:
    route = args[1]
    symbol = args[2]
else:
    exit("ERROR: No symbol or route supplied in " + sys.argv[0])

url = 'XXXXX.amazonaws.com/c' + str(route) + '?symbol=' + symbol

response = requests.get(url, timeout=20)

json_data = response.json() if response and response.status_code == 200 else None

if json_data and 'Symbol' in json_data:
    company_data = {
        'symbol': json_data['Symbol'],
        'name': json_data['Name'],
        'currency': json_data['Currency'],
        'country':  json_data['Country'],
        'sector':   json_data['Sector'],
        'industry': json_data['Industry'],
        'exchange': json_data['Exchange'],
        'asset_type': json_data['AssetType'],
        'cik':      json_data['CIK'],
        'address': json_data['Address'],
        'market_cap': json_data['MarketCapitalization'],
        'pe': json_data['PERatio'],
        'bookvalue': json_data['BookValue'],
        'divps': json_data['DividendPerShare'],
        'divyield': json_data['DividendYield'],
        'eps': json_data['EPS'],
        'analyst_price_target': json_data['AnalystTargetPrice'],
        'price_to_book': json_data['PriceToBookRatio'],
        'beta': json_data['Beta'],
        'shares': json_data['SharesOutstanding'],
        'divdate': json_data['DividendDate'],
        'exdivdate': json_data['ExDividendDate']
    }
    company = Table('company', metadata, autoload_with=engine)
    statement = delete(company).where(company.c.symbol == symbol)
    result = engine.execute(statement)
    
    statement = insert(company, company_data)
    result = engine.execute(statement)
    
elif json_data and 'Error Message' in json_data:
    ignored = Table('ignored', metadata, autoload_with=engine)
    statement = insert(ignored, {"symbol": symbol, "ignored": datetime.now()})
    result = engine.execute(statement)
    print("   ---> invalid API call for symbol " + symbol + ". Added to ignored")
    exit()
elif json_data and ('Information' in json_data or 'Note' in json_data):
    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%m")
    print("   ---> rate limit reached")
elif json_data == None:
    print("   ---> null response object for symbol " + symbol + ": " + str(response))
    exit()
elif len(json_data) == 0:
    ignored = Table('ignored', metadata, autoload_with=engine)
    statement = insert(ignored, {"symbol": symbol, "ignored": datetime.now()})
    result = engine.execute(statement)
    print("   ---> no data found in response for symbol " + symbol + ". Added to ignored")
    exit()
else:
    print("   ---> data: " + str(json_data))
    exit()
