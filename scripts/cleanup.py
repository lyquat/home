import shutil
import os
import requests
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update, func
import csv, urllib.request

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

now = datetime.now()

WWW_DIRECTORY = "/home/public_html/"

inserts = []

ignored = Table('ignored', metadata, autoload_with=engine)

listing_status = Table('listing_status', metadata, autoload_with=engine)
audit_log = Table('audit_log', metadata, autoload_with=engine)
company = Table('company', metadata, autoload_with=engine)
industry = Table('industry', metadata, autoload_with=engine)
company_sector_industry = Table('company_sector_industry', metadata, autoload_with=engine)
company_supplementary = Table('company_supplementary', metadata, autoload_with=engine)
earnings = Table('earnings', metadata, autoload_with=engine)
earnings_calendar = Table('earnings_calendar', metadata, autoload_with=engine)
balance_sheet = Table('balance_sheet', metadata, autoload_with=engine)
cashflow = Table('cashflow', metadata, autoload_with=engine)
income_statement = Table('income_statement', metadata, autoload_with=engine)
time_series_weekly_adjusted = Table('time_series_weekly_adjusted', metadata, autoload_with=engine)
time_series_daily = Table('time_series_daily', metadata, autoload_with=engine)
balance_sheet_annuals = Table('balance_sheet_annuals', metadata, autoload_with=engine)
cashflow_annuals = Table('cashflow_annuals', metadata, autoload_with=engine)
earnings_annuals = Table('earnings_annuals', metadata, autoload_with=engine)
income_statement_annuals = Table('income_statement_annuals', metadata, autoload_with=engine)

print("Deleting audit symbols not in listing_status...first insert into ignored, then delete from")
query = select(audit_log.c.symbol).\
where(audit_log.c.symbol.notin_(select(listing_status.c.symbol)))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    try:
        result = engine.execute(statement)
    except:
        print(symbol + " already in ignored")

    statement = delete(ignored).where(ignored.c.symbol == symbol)
    result = engine.execute(statement)
    
print("Deleting company supplementary if not in company")
statement = delete(company_supplementary).\
where(company_supplementary.c.symbol.notin_(select(company.c.symbol)))
result = engine.execute(statement)

print("Deleting financials > 6 years")
diff = date.today() - timedelta(days=6*365)
statement = delete(balance_sheet).where(balance_sheet.c.fiscalDateEnding < diff)
result = engine.execute(statement)
statement = delete(cashflow).where(cashflow.c.fiscalDateEnding < diff)
result = engine.execute(statement)
statement = delete(income_statement).where(income_statement.c.fiscalDateEnding < diff)
result = engine.execute(statement)

print("Deleting earnings > 11 years")
diff = date.today() - timedelta(days=11*365)
statement = delete(earnings).where(earnings.c.fiscalDateEnding < diff)
result = engine.execute(statement)

print("Deleting audit log if not in ignored and not in company")
query = select(audit_log.c.symbol).\
where(audit_log.c.symbol.notin_(select(company.c.symbol))).\
where(audit_log.c.symbol.notin_(select(ignored.c.symbol)))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    statement = delete(audit_log).where(audit_log.c.symbol == symbol)
    result = engine.execute(statement)

print("Deleting audit log if in ignored")
query = select(audit_log.c.symbol).\
where(audit_log.c.symbol.in_(select(ignored.c.symbol)))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    statement = delete(audit_log).where(audit_log.c.symbol == symbol)
    result = engine.execute(statement)

print("Deleting audit log if not in company")
query = select(audit_log.c.symbol).\
where(audit_log.c.symbol.notin_(select(company.c.symbol)))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    statement = delete(audit_log).where(audit_log.c.symbol == symbol)
    result = engine.execute(statement)
    
print("Insert symbols > len(4) where left(symbol,4) exists into ignored")
query = select(audit_log.c.symbol).\
where(func.length(audit_log.c.symbol) > 4).\
where(func.left(audit_log.c.symbol,4).in_(select(audit_log.c.symbol).where(func.length(audit_log.c.symbol) == 4)))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert blank checks into ignored")
query = select(company.c.symbol).\
where(company.c.industry == 'BLANK CHECKS')
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert acquisition into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Acquisition'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert SPAC into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('SPAC'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'notes due' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Notes due'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'merger corp' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Merger Corp'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'Opportunity corp' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Opportunity Corp'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)
    
print("Insert '%W' > len(4) into ignored")
query = select(company.c.symbol).\
where(func.length(company.c.symbol)>4).\
where(company.c.symbol.endswith('W'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'warrant' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Warrant'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert '%' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('\%'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)
    
print("Insert ending in '-WS' into ignored")
query = select(company.c.symbol).\
where(company.c.symbol.endswith('-WS'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)
    
print("Insert ending in '-W' into ignored")
query = select(company.c.symbol).\
where(company.c.symbol.endswith('-W'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)
    
print("Insert ending in '-R-W' into ignored")
query = select(company.c.symbol).\
where(company.c.symbol.endswith('-R-W'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)
    
print("Insert contains '-P-' into ignored")
query = select(company.c.symbol).\
where(company.c.symbol.contains('-P-'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'Unsecured notes' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('Unsecured Notes'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Insert 'WT EXP' into ignored")
query = select(company.c.symbol).\
where(company.c.name.contains('WT EXP'))
result = engine.execute(query)
for row in result:
    symbol = row[0]
    q = {"symbol": symbol, "ignored": datetime.now()}
    statement = insert(ignored, q)
    result = engine.execute(statement)

print("Delete symbols from " + WWW_DIRECTORY + " if in ignored")
query = select(ignored.c.symbol)
result = engine.execute(query)
for row in result:
    symbol = row[0]
    path = WWW_DIRECTORY + symbol
    exists = os.path.exists(path)
    if exists:
        print("Directory " + path + " exists - deleting...")
        shutil.rmtree(path)
        
print("Delete industries from " + WWW_DIRECTORY + " if not in companies")
query = select(industry.c.industryid).where(industry.c.industryid.not_in(select(company_sector_industry.c.industryid)))
result = engine.execute(query)
for row in result:
    industryid = row[0]
    path = WWW_DIRECTORY + str(industryid)
    exists = os.path.exists(path)
    if exists:
        print("Directory " + path + " exists - deleting...")
        shutil.rmtree(path)

#print("Delete earnings calendars older than 60 days")
#statement = delete(earnings_calendar).where(earnings_calendar.c.report_date != None).where(func.datediff(earnings_calendar.c.report_date, now) < -60)
#result = engine.execute(statement)

print("Delete forecast earnings older than current date")
statement = delete(earnings_calendar).where(earnings_calendar.c.report_date != None).where(earnings_calendar.c.report_date < now)
result = engine.execute(statement)

then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")
