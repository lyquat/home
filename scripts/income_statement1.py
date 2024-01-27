import sys
import requests
import subprocess
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
    #url = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&apikey=' + key + '&symbol=' + symbol
    url = 'XXXXX.amazonaws.com/in' + str(rand) + '?symbol=' + symbol

#print(url)
exit
response = requests.get(url, timeout=10)

json_data = response.json() if response and response.status_code == 200 else None

current_datetime = str(date.today())

def get_income_data(e):
    income_statement_data = {
            'symbol': symbol,
            'fiscalDateEnding': e['fiscalDateEnding'],
            'reportedCurrency': e['reportedCurrency'],
            'grossProfit': e['grossProfit'],
            'totalRevenue': e['totalRevenue'],
            'costOfRevenue': e['costOfRevenue'],
            'costofGoodsAndServicesSold': e['costofGoodsAndServicesSold'],
            'operatingIncome': e['operatingIncome'],
            'sellingGeneralAndAdministrative': e['sellingGeneralAndAdministrative'],
            'researchAndDevelopment': e['researchAndDevelopment'],
            'operatingExpenses': e['operatingExpenses'],
            'investmentIncomeNet': e['investmentIncomeNet'],
            'netInterestIncome': e['netInterestIncome'],
            'interestIncome': e['interestIncome'],
            'interestExpense': e['interestExpense'],
            'nonInterestIncome': e['nonInterestIncome'],
            'otherNonOperatingIncome': e['otherNonOperatingIncome'],
            'depreciation': e['depreciation'],
            'depreciationAndAmortization': e['depreciationAndAmortization'],
            'incomeBeforeTax': e['incomeBeforeTax'],
            'incomeTaxExpense': e['incomeTaxExpense'],
            'interestAndDebtExpense': e['interestAndDebtExpense'],
            'netIncomeFromContinuingOperations': e['netIncomeFromContinuingOperations'],
            'comprehensiveIncomeNetOfTax': e['comprehensiveIncomeNetOfTax'],
            'ebit': e['ebit'],
            'ebitda': e['ebitda'],
            'netIncome': e['netIncome'],
            'last_updated': current_datetime
        }
    return income_statement_data

if json_data and 'quarterlyReports' in json_data:

    inserts = []
    income_statement = Table('income_statement', metadata, autoload_with=engine)

    income_statement_quarterly = json_data['quarterlyReports']
    for e in income_statement_quarterly:
        income_statement_data = get_income_data(e)
        inserts.append(income_statement_data)

    if len(inserts)>0:
        statement = delete(income_statement).where(income_statement.c.symbol == symbol)
        engine.execute(statement)
        ins = income_statement.insert()
        engine.execute(ins, inserts)

    inserts = []
    income_statement_annuals = Table('income_statement_annuals', metadata, autoload_with=engine)

    income_statement_annual_data = json_data['quarterlyReports']
    for e in income_statement_annual_data:
        income_statement_data = get_income_data(e)
        inserts.append(income_statement_data)

    if len(inserts)>0:
        statement = delete(income_statement_annuals).where(income_statement_annuals.c.symbol == symbol)
        engine.execute(statement)
        ins = income_statement_annuals.insert()
        engine.execute(ins, inserts)
        
elif json_data and 'Invalid API call' in json_data:
    print("   ---> invalid API call")
    exit(1)
elif json_data and ('Information' in json_data or 'Note' in json_data):
    print(json_data)
    print("   ---> Rate limited. Exiting")
    #subprocess.call(" python3 income_statement2.py " + symbol, shell=True)
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
