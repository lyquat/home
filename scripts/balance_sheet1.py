import sys
import os
import requests
import subprocess
import random
from datetime import datetime, date
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update

url = ''
symbol = None
args = sys.argv
if len(args) == 3:
    # print("Usage: " + args[0]+ " [symbol]")
    key = args[1]
    symbol = args[2]
    rand = random.randint(1, 4)
    #url = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&apikey=' + key + '&symbol=' + symbol
    url = 'XXXXX.amazonaws.com/bs' + str(rand) + '?symbol=' + symbol

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

response = requests.get(url, timeout=20)

json_data = response.json() if response and response.status_code == 200 else None

current_datetime = str(date.today())

def get_balance_sheet_data(e):
    balance_sheet_data = {
            'symbol': symbol,
            'fiscalDateEnding': e['fiscalDateEnding'],
            'reportedCurrency': e['reportedCurrency'],
            'totalAssets': e['totalAssets'],
            'totalCurrentAssets': e['totalCurrentAssets'],
            'cashAndCashEquivalentsAtCarryingValue': e['cashAndCashEquivalentsAtCarryingValue'],
            'cashAndShortTermInvestments': e['cashAndShortTermInvestments'],
            'inventory': e['inventory'],
            'currentNetReceivables': e['currentNetReceivables'],
            'totalNonCurrentAssets': e['totalNonCurrentAssets'],
            'propertyPlantEquipment': e['propertyPlantEquipment'],
            'accumulatedDepreciationAmortizationPPE': e['accumulatedDepreciationAmortizationPPE'],
            'intangibleAssets': e['intangibleAssets'],
            'intangibleAssetsExcludingGoodwill': e['intangibleAssetsExcludingGoodwill'],
            'goodwill': e['goodwill'],
            'investments': e['investments'],
            'longTermInvestments': e['longTermInvestments'],
            'shortTermInvestments': e['shortTermInvestments'],
            'otherCurrentAssets': e['otherCurrentAssets'],
            'otherNonCurrrentAssets': e['otherNonCurrentAssets'],
            'totalLiabilities': e['totalLiabilities'],
            'totalCurrentLiabilities': e['totalCurrentLiabilities'],
            'currentAccountsPayable': e['currentAccountsPayable'],
            'deferredRevenue': e['deferredRevenue'],
            'currentDebt': e['currentDebt'],
            'shortTermDebt': e['shortTermDebt'],
            'totalNonCurrentLiabilities': e['totalNonCurrentLiabilities'],
            'capitalLeaseObligations': e['capitalLeaseObligations'],
            'longTermDebt': e['longTermDebt'],
            'currentLongTermDebt': e['currentLongTermDebt'],
            'longTermDebtNoncurrent': e['longTermDebtNoncurrent'],
            'shortLongTermDebtTotal': e['shortLongTermDebtTotal'],
            'otherCurrentLiabilities': e['otherCurrentLiabilities'],
            'otherNonCurrentLiabilities': e['otherNonCurrentLiabilities'],
            'totalShareholderEquity': e['totalShareholderEquity'],
            'treasuryStock': e['treasuryStock'],
            'retainedEarnings': e['retainedEarnings'],
            'commonStock': e['commonStock'],
            'commonStockSharesOutstanding': e['commonStockSharesOutstanding']
        }
    return balance_sheet_data

if json_data and 'quarterlyReports' in json_data:
    symbol = json_data['symbol']

    balance_sheet = Table('balance_sheet', metadata, autoload_with=engine)

    inserts = []
    balance_sheet_quarterly = json_data['quarterlyReports']
    for e in balance_sheet_quarterly:
        balance_sheet_data = get_balance_sheet_data(e)
        inserts.append(balance_sheet_data)

    if len(inserts)>0:
        statement = delete(balance_sheet).where(balance_sheet.c.symbol == symbol)
        engine.execute(statement)
        ins = balance_sheet.insert()
        engine.execute(ins, inserts)

    balance_sheet_annuals = Table('balance_sheet_annuals', metadata, autoload_with=engine)

    inserts = []
    balance_sheet_quarterly = json_data['annualReports']
    for e in balance_sheet_quarterly:
        balance_sheet_data = get_balance_sheet_data(e)
        inserts.append(balance_sheet_data)

    if len(inserts)>0:
        statement = delete(balance_sheet_annuals).where(balance_sheet_annuals.c.symbol == symbol)
        engine.execute(statement)
        ins = balance_sheet_annuals.insert()
        engine.execute(ins, inserts)

elif json_data and 'Invalid API call' in json_data:
    print("   ---> invalid API call")
    exit(1)
elif json_data and ('Information' in json_data or 'Note' in json_data):
    print(json_data)
    print("   ---> Rate limited. Exiting")
    #subprocess.call(" python3 balance_sheet2.py " + symbol, shell=True)
    exit(1)
elif json_data == None:
    print("   ---> null response")
    exit(1)
elif json_data == None:
    print("   ---> null response for symbol " + symbol)
    exit(1)
elif len(json_data) == 0:
    print("   ---> no data found in response")
    exit(1)
else:
    print("   ---> data: " + str(json_data))
    exit(1)
