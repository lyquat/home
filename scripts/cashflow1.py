import sys
import requests
import subprocess
import logging
import random
from datetime import datetime, date
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

url = ''
symbol = None
args = sys.argv
if len(args) == 3:
    key = args[1]
    symbol = args[2]
    rand = random.randint(1, 4)
    #url = 'https://www.alphavantage.co/query?function=CASH_FLOW&apikey=' + key + '&symbol=' + symbol
    url = 'XXXXX.amazonaws.com/cf' + str(rand) + '?symbol=' + symbol

response = requests.get(url, timeout=10)

json_data = response.json() if response and response.status_code == 200 else None

current_datetime = str(date.today())

def get_cashflow_data(e):
    cashflow_data = {
            "symbol": symbol or None,
            "fiscalDateEnding": e["fiscalDateEnding"] or None,
            "reportedCurrency": e["reportedCurrency"] or None,
            "operatingCashflow": e["operatingCashflow"] or None,
            "paymentsForOperatingActivities": e["paymentsForOperatingActivities"] or None,
            "proceedsFromOperatingActivities": e["proceedsFromOperatingActivities"] or None,
            "changeInOperatingLiabilities": e["changeInOperatingLiabilities"] or None,
            "changeInOperatingAssets": e["changeInOperatingAssets"] or None,
            "depreciationDepletionAndAmortization": e["depreciationDepletionAndAmortization"] or None,
            "capitalExpenditures": e["capitalExpenditures"] or None,
            "changeInReceivables": e["changeInReceivables"] or None,
            "changeInInventory": e["changeInInventory"] or None,
            "profitLoss": e["profitLoss"] or None,
            "cashflowFromInvestment": e["cashflowFromInvestment"] or None,
            "cashflowFromFinancing": e["cashflowFromFinancing"] or None,
            "proceedsFromRepaymentsOfShortTermDebt": e["proceedsFromRepaymentsOfShortTermDebt"] or None,
            "paymentsForRepurchaseOfCommonStock": e["paymentsForRepurchaseOfCommonStock"] or None,
            "paymentsForRepurchaseOfEquity": e["paymentsForRepurchaseOfEquity"] or None,
            "paymentsForRepurchaseOfPreferredStock": e["paymentsForRepurchaseOfPreferredStock"] or None,
            "dividendPayout": e["dividendPayout"] or None,
            "dividendPayoutCommonStock": e["dividendPayoutCommonStock"] or None,
            "dividendPayoutPreferredStock": e["dividendPayoutPreferredStock"] or None,
            "proceedsFromIssuanceOfCommonStock": e["proceedsFromIssuanceOfCommonStock"] or None,
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": e["proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet"] or None,
            "proceedsFromIssuanceOfPreferredStock": e["proceedsFromIssuanceOfPreferredStock"] or None,
            "proceedsFromRepurchaseOfEquity": e["proceedsFromRepurchaseOfEquity"] or None,
            "proceedsFromSaleOfTreasuryStock": e["proceedsFromSaleOfTreasuryStock"] or None,
            "changeInCashAndCashEquivalents": e["changeInCashAndCashEquivalents"] or None,
            "changeInExchangeRate": e["changeInExchangeRate"] or None,
            "netIncome": e["netIncome"] or None
        }
    return cashflow_data

if json_data and 'quarterlyReports' in json_data:

    cashflow = Table('cashflow', metadata, autoload_with=engine)
    
    inserts = []
    cashflow_quarterly = json_data["quarterlyReports"]
    for e in cashflow_quarterly:
        cashflow_data = get_cashflow_data(e)
        inserts.append(cashflow_data)
    
    if len(inserts)>0:
        statement = delete(cashflow).where(cashflow.c.symbol == symbol)
        engine.execute(statement)
        ins = cashflow.insert()
        engine.execute(ins, inserts)

    cashflow_annuals = Table('cashflow_annuals', metadata, autoload_with=engine)

    inserts = []

    cashflow_annuals_data = json_data['annualReports']
    for e in cashflow_annuals_data:
        cashflow_data = get_cashflow_data(e)
        inserts.append(cashflow_data)

    if len(inserts)>0:
        statement = delete(cashflow_annuals).where(cashflow_annuals.c.symbol == symbol)
        engine.execute(statement)
        ins = cashflow_annuals.insert()
        engine.execute(ins, inserts)

elif json_data and 'Invalid API call' in json_data:
    print("   ---> invalid API call")
    exit(1)
elif json_data and ('Information' in json_data or 'Note' in json_data):
    print(json_data)
    print("   ---> Rate limited. Exiting")
    #subprocess.call(" python3 cashflow2.py " + symbol, shell=True)
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
