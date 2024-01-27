from datetime import datetime, timedelta
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import make_response
from flask import session
from flask import flash
from flask import abort, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy import inspect
from sqlalchemy.engine import reflection
from sqlalchemy.sql import select, text, func
import jinja2
import lyquat_filters
from lyquat_filters import human_format
from lyquat_filters import changepct, pad_cik
from lyquat_filters import color, swap_sort
from lyquat_filters import from_camelcase
from lyquat_filters import format_2dp, escape_backslash
from lyquat_filters import thousands, millions
from lyquat_filters import country
from lyquat_filters import date_string
from lyquat_queries import gainers, monthly_prices_from_weekly, q_rev_earnings, q_debt
from lyquat_queries import unique_sectors
from lyquat_queries import q_snapshot
from lyquat_queries import q_companies, q_company_stats, q_earnings
from lyquat_queries import q_free_cashflow, q_earnings_calendar
from lyquat_queries import q_weeklies, q_dailies
from lyquat_queries import q_shares_outstanding, q_price_to_book
from lyquat_queries import earnings_surprises, q_market_cap_income_statement
from lyquat_queries import industries_for_sector, q_historical_changepct, q_price_changes
from lyquat_queries import q_balance_sheet, q_cashflows, q_income_statement, q_market_cap_balance_sheet
from lyquat_queries import q_unique_industries
from lyquat_queries import q_supps
from lyquat_queries import q_lookup
from lyquat_queries import q_upcoming_earnings_calendar
from lyquat_queries import q_upcoming_earnings_calendar_min_max

app = Flask(__name__)

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

app.jinja_env.filters.update(human_format = human_format)
app.jinja_env.filters.update(changepct = changepct)
app.jinja_env.filters.update(color = color)
app.jinja_env.filters.update(from_camelcase = from_camelcase)
app.jinja_env.filters.update(format_2dp=format_2dp)
app.jinja_env.filters.update(thousands=thousands)
app.jinja_env.filters.update(millions=millions)
app.jinja_env.filters.update(swap_sort=swap_sort)
app.jinja_env.filters.update(escape_backslash=escape_backslash)
app.jinja_env.filters.update(pad_cik=pad_cik)
app.jinja_env.filters.update(country=country)
app.jinja_env.filters.update(date_string=date_string)

def get_overview_data(symbol):
    table = Table('company_sector_industry', metadata, autoload=True)
    query, limit, offset = q_companies(engine, metadata)
    query = query.where(table.c.symbol == symbol)
    # print(query)

    results = engine.execute(query)
    company = None
    for row in results:
        company = {"symbol": row[0], "name": row[1], "sector": row[2], "industry": row[3], "exchange": row[4], "market_cap": row[5], "industry_id": row[6], "cik": row[7], "sectorid": row[8]}

    query_stats = q_company_stats(engine, metadata, symbol)

    stats_results = engine.execute(query_stats)
    stats = None
    for row in stats_results:
        stats = {"pe": row[1], "bookvalue": row[2], "divps": row[3], "divyield": row[4], "eps": row[5], "analyst_price_target": row[6], "price_to_book": row[7], "beta": row[8], "shares": row[9], "divdate": row[10], "exdivdate": row[11]}
    return company, stats
    
@app.route('/query')
def query():
    return redirect("http://lyquat.com/query")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_error(error):
    return render_template('500.html'), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/<symbol>/')
def symbol(symbol):
    company, stats = get_overview_data(symbol)
    if company is None:
        return render_template('404.html'), 404
    name = company['name']

    query = q_balance_sheet(engine, metadata, symbol)
    bs_keys, bs_data, bs_periods, bs_currencies = [],[],[],[]
    result = engine.execute(query)
    for x in result.keys():
        foo = q_lookup(engine, metadata, "balance_sheet", x)
        bar = engine.execute(foo)
        y = None
        for row in bar:
            order = row.order_id
            y = {"key": x, "order": order}

        bs_keys.append(y)

    del bs_keys[0] # symbol
    del bs_keys[0] # fiscaldateending
    del bs_keys[0] # reportedCurrency

    for row in result:
        bs_periods.append(row[1])
        bs_currencies.append(row[2])
        bs_data.append(row[3:len(row)])

    query = q_income_statement(engine, metadata, symbol)
    is_keys, is_data, is_periods, is_currencies = [],[],[],[]
    result = engine.execute(query)
    for x in result.keys():
        foo = q_lookup(engine, metadata, "income_statement", x)
        bar = engine.execute(foo)
        y = None
        for row in bar:
            order = row.order_id
            y = {"key": x, "order": order}
            
        is_keys.append(y)

    del is_keys[0] # symbol
    del is_keys[0] # fiscaldateending
    del is_keys[0] # reportedCurrency

    for row in result:
        is_periods.append(row[1])
        is_currencies.append(row[2])
        is_data.append(row[3:len(row)])

    query = q_cashflows(engine, metadata, symbol)
    cf_keys, cf_data, cf_periods, cf_currencies = [],[],[],[]
    result = engine.execute(query)
    for x in result.keys():
        cf_keys.append(x)

    del cf_keys[0] # symbol
    del cf_keys[0] # fiscaldateending
    del cf_keys[0] # reportedCurrency

    for row in result:
        cf_periods.append(row[1])
        cf_currencies.append(row[2])
        cf_data.append(row[3:len(row)])

    currentDateTime = datetime.now()
    date = currentDateTime.date()
    min_year = int(date.strftime("%Y"))
    max_year = int(min_year) + 10

    query = q_free_cashflow(symbol, engine, metadata)
    results = engine.execute(query)
    fcf = []
    for row in results:
        market_cap = row[1]
        tmp = {"symbol": row[0], "market_cap": row[1], "fiscalDateEnding": row[2], "currency": row[3], "operatingCashflow": row[4], "capitalExpenditures": row[5], "fcf_using_operating_cashflow": row[6], "cash_and_cash_equivalents": row[7]}
        fcf.append(tmp)
        
    query = q_supps(engine, metadata, symbol)
    results = engine.execute(query)
    supps = {}
    for row in results:
        country = row[0]
        logo_url = row[1]
        website = row[2]
        supps = {"country": country, "logo_url" : logo_url, "website": website}

    return render_template('symbol.html', company=company, stats=stats, symbol=symbol, title=name, balance_sheet_data=bs_data, balance_sheet_currencies=bs_currencies, balance_sheet_periods=bs_periods, balance_sheet_keys=bs_keys, income_statement_data=is_data, income_statement_currencies=is_currencies, income_statement_periods=is_periods, income_statement_keys=is_keys, cashflows_data=cf_data, cashflows_currencies=cf_currencies, cashflows_periods=cf_periods, cashflows_keys=cf_keys, min_year=min_year, max_year=max_year, fcf=fcf, supps=supps)

@app.route("/")
def index():
    query = q_snapshot(engine, metadata, request.args)
    result = engine.execute(query)
    rows = []
    for row in result:
        x = {"sector": row[0], "industry": row[1], "count": row[2], "market_cap": row[3], "industry_id": row[4], "min": row[5], "max": row[6], "sectorid": row[7]}
        rows.append(x)

    unique_sectors = get_sectors()

    return render_template('snapshot.html', rows=rows, sectors=unique_sectors)

@app.route("/sector/<sectorid>/")
def snapshot_by_sector(sectorid):
    snapshot = Table('snapshot', metadata, autoload=True)
    sector = Table('sector', metadata, autoload=True)
    query = q_snapshot(engine, metadata, request.args)
    query = query.filter(sector.c.sectorid == sectorid)
    result = engine.execute(query)
    rows = []
    for row in result:
        x = {"sector": row[0], "industry": row[1], "count": row[2], "market_cap": row[3], "industry_id": row[4], "min": row[5], "max": row[6], "sectorid": row[7]}
        rows.append(x)

    unique_sectors = get_sectors()

    return render_template('snapshot.html', rows=rows, sectors=unique_sectors)

@app.route("/list/<industry>/")
def list_industry(industry):
    company = Table('company_sector_industry', metadata, autoload=True)
    query, limit, offset = q_companies(engine, metadata)
    query = query.filter(company.c.industryid == industry)
    result = engine.execute(query)
    companies = []
    for row in result:
        x = {"symbol": row[0], "name": row[1], "sector": row[2], "industry": row[3], "exchange": row[4], "market_cap": row[5], "industry_id": row[6], "cik": row[7], "sectorid": row[8], "country": row[9], "asset_type": row[10], "pe": row[11], "bookvalue": row[12], "price_to_book": row[13], "eps": row[14], "analyst_price_target": row[15]}
        companies.append(x)

    return render_template('list.html', companies=companies, industryid=industry)
    
@app.route('/list/<industry>/list.js')
def js_list(industry):
    company = Table('company_sector_industry', metadata, autoload=True)
    query, limit, offset = q_companies(engine, metadata)
    query = query.filter(company.c.industryid == industry)
    result = engine.execute(query)

    companies_tmp = []
    for row in result:
        x = {"symbol": row[0]}
        companies_tmp.append(x)

    company_prices = []

    for c in companies_tmp:
        symbol = c['symbol']
        query = q_weeklies(engine, metadata, symbol)
        result = engine.execute(query)
        weeklies = []
        for row in result:
            week_ending = row[1]
            adjusted_close = row[2]
            x = {"week_ending": week_ending, "adjusted_close": adjusted_close}
            weeklies.append(x)

        x = {"symbol": symbol, "prices": weeklies}
        company_prices.append(x)

    return render_template('list.js', company_prices=company_prices), 200, {'Content-Type': 'application/javascript; charset=utf-8'}


@app.route('/<symbol>/code.js')
def js(symbol):
    query = q_weeklies(engine, metadata, symbol)
    result = engine.execute(query)
    weeklies = []
    for row in result:
        week_ending = row[1]
        adjusted_close = row[2]
        x = {"week_ending": week_ending, "adjusted_close": adjusted_close}
        weeklies.append(x)

    query = q_earnings(engine, metadata, symbol)
    result = engine.execute(query)
    earnings_history = []
    for row in result:
        x = {"fiscalDateEnding": row[1], "reportedDate": row[2], "reportedEPS": row[3], "estimatedEPS": row[4]}
        earnings_history.append(x)

    query = q_earnings_calendar(engine, metadata, symbol)
    result = engine.execute(query)
    earnings_forecast = []
    for row in result:
        x = {"fiscal_date_ending": row[1], "report_date": row[2], "forecastEPS": row[3]}
        earnings_forecast.append(x)

    query = q_shares_outstanding(symbol, engine, metadata)
    results = engine.execute(query)

    shares = []
    for row in results:
        tmp = {"period": row[0], "shares_outstanding": row[1]}
        shares.append(tmp)

    monthly_query = monthly_prices_from_weekly(symbol, engine, metadata, 52)
    result = engine.execute(monthly_query)
    ytd = []
    for row in result:
        year = row[1]
        month = row[2]
        d = str(datetime(year, month, 1))
        min = row[3]
        max = row[4]
        r = {"date": d, "min": min, "max": max}
        ytd.append(r)

    query = q_market_cap_balance_sheet(engine, metadata, symbol)
    result = engine.execute(query)
    balance_sheet = []
    market_cap = 0
    for row in result:
        market_cap = row[1]
        data = { "symbol": row[0], "market_cap": row[1], "period": row[2], "currency": row[3], "totalAssets": row[4], "cash": row[5], "totalLiabilities": row[6], "longTermDebt": row[7]}
        balance_sheet.append(data)

    query = q_market_cap_income_statement(engine, metadata, symbol)
    result = engine.execute(query)
    income_statement = []
    market_cap = 0
    for row in result:
        market_cap = row[1]
        data = { "symbol": row[0], "market_cap": row[1], "period": row[2], "currency": row[3], "totalrevenue": row[4], "costofrevenue": row[5], "grossprofit": row[6], "operatingincome": row[7], "sellinggeneralandadministrative": row[8], "operatingexpenses": row[9], "interestincome": row[10], "netinterestincome": row[11], "interestexpense": row[12], "depreciationandamortization": row[13], "incomebeforetax": row[14], "incometaxexpense": row[15], "ebit": row[16], "ebitda": row[17], "netincome": row[18]}
        income_statement.append(data)

    return render_template('code.js', symbol=symbol, weeklies=weeklies, earnings_history=earnings_history, earnings_forecast=earnings_forecast, shares=shares, ytd=ytd, balance_sheet=balance_sheet, income_statement=income_statement), 200, {'Content-Type': 'application/javascript; charset=utf-8'}

def get_sectors():

    query = unique_sectors(engine, metadata)
    result = engine.execute(query)
    sectors = []
    for row in result:
        x = {"sector": row[0], "sectorid": row[1]}
        sectors.append(x)

    return sectors
    
@app.route('/calendar/')
def calendar():
    q_min_max = q_upcoming_earnings_calendar_min_max(engine, metadata)
    current_date = datetime.now()
    result = engine.execute(q_min_max)
    r_min = None
    r_max = None
    for r in result:
        r_min = r[0]
        r_max = r[1]
        
    step = timedelta(days=1)
    while(r_min.isoweekday() != 1): # Monday
        r_min = r_min - step

    while(r_max.isoweekday() != 1): # Monday
        r_max = r_max - step

    step = timedelta(weeks=1)
    weeks = []
    weeks.append(r_min)
    while r_max not in weeks:
        r_min = r_min + step
        weeks.append(r_min)
        
    data = {k: [] for k in weeks}
    query = q_upcoming_earnings_calendar(engine, metadata)
    result = engine.execute(query)
    for row in result:
        symbol = row[0]
        name = row[1]
        sectorid = int(row[2])
        sector = row[3]
        report_date = row[4]
        estimate = row[5]
        last_eps = row[6]
        report_date_iso = report_date.isoweekday()
        monday_of = report_date
        if report_date_iso != 1: # Monday
          while monday_of.isoweekday() != 1:
                monday_of = monday_of - timedelta(days=1)

        x = {"symbol": symbol, "report_date": report_date, "sectorid": sectorid, "estimate": estimate, "last_eps": last_eps, "report_date_iso": report_date_iso}
        foo = data[monday_of]
        data.get(monday_of).append(x)

    return render_template('calendar.html', data=data)
