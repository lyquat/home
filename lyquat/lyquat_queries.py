from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy import inspect
from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import between
from sqlalchemy import asc, desc
from sqlalchemy import cast, Numeric
from sqlalchemy.sql import select, text
from datetime import datetime, timedelta

def apply_company_filters(the_query, company, args):
    query = the_query
    if args is not None:
        industry = args.get('industry', '')
        if industry:
            query = query.where(company.c.industry == industry)

        sector = args.get('sector', '')
        if sector:
            query = query.where(company.c.sector == sector)

        country = args.get('country', '')
        if country:
            query = query.where(company.c.country == country)
    return query
    
def q_supps(engine, metadata, symbol):
    company_supp = Table('company_supplementary', metadata, autoload_with=engine)
    query = select(company_supp.c.country, company_supp.c.logo_url, company_supp.c.website).where(company_supp.c.symbol == symbol)
    return query

def q_earnings(engine, metadata, symbol):
    ev = Table('earnings', metadata, autoload_with=engine)
    query = select(ev.c.symbol, ev.c.fiscalDateEnding, ev.c.reportedDate, ev.c.reportedEPS, ev.c.estimatedEPS).\
    where(ev.c.symbol == symbol)
    return query

def q_earnings_calendar(engine, metadata, symbol):
    ec = Table('earnings_calendar', metadata, autoload_with=engine)
    query = select(ec.c.symbol, ec.c.fiscal_date_ending, ec.c.report_date, ec.c.estimate, ec.c.currency).\
    where(ec.c.symbol == symbol)
    return query
    
def q_lookup(engine, metadata, table_name, field_name):
    lookups = Table('lookups', metadata, autoload_with=engine)
    query = select(lookups.c.field, lookups.c.order_id).where(lookups.c.table_name == table_name).where(lookups.c.field == field_name)
    return query

def q_balance_sheet(engine, metadata, symbol):
    balance_sheet = Table('balance_sheet', metadata, autoload_with=engine)
    query = select([col for col in balance_sheet.columns]).where(balance_sheet.c.symbol == symbol).order_by(desc(balance_sheet.c.fiscalDateEnding))
    return query

def q_income_statement(engine, metadata, symbol):
    income_statement = Table('income_statement', metadata, autoload_with=engine)
    query = select([col for col in income_statement.columns]).where(income_statement.c.symbol == symbol).order_by(desc(income_statement.c.fiscalDateEnding))
    return query

def q_cashflows(engine, metadata, symbol):
    cashflow = Table('cashflow', metadata, autoload_with=engine)
    query = select([col for col in cashflow.columns]).where(cashflow.c.symbol == symbol).order_by(desc(cashflow.c.fiscalDateEnding))
    return query

def q_sector_stats(engine, metadata, args=None):
    company = Table('company', metadata, autoload=True)
    query = select(company.c.sector, func.count(company.c.sector), func.sum(company.c.market_cap)).\
    group_by(company.c.sector)
    return query

def q_snapshot(engine, metadata, args=None):
    snapshot = Table('snapshot', metadata, autoload=True)
    industry = Table('industry', metadata, autoload=True)
    sector = Table('sector', metadata, autoload=True)
    query = select(snapshot.c.sector, snapshot.c.industry, snapshot.c.total, snapshot.c.market_cap, industry.c.industryid, snapshot.c.min, snapshot.c.max, sector.c.sectorid).\
    join(industry, snapshot.c.industry == industry.c.industry).\
    join(sector, sector.c.sector == snapshot.c.sector).\
    order_by(snapshot.c.sector, snapshot.c.industry)
    return query

def q_companies(engine, metadata, args=None, alimit=None, offset=None):
    company = Table('company_sector_industry', metadata, autoload=True)
    sector = Table('sector', metadata, autoload=True)
    query = select(company.c.symbol, company.c.name, company.c.sector, company.c.industry, company.c.exchange, company.c.market_cap, company.c.industryid, company.c.cik, sector.c.sectorid, company.c.country, company.c.asset_type, company.c.pe, company.c.bookvalue, company.c.price_to_book, company.c.eps, company.c.analyst_price_target).\
    join(sector, sector.c.sector == company.c.sector)

    return query, alimit, offset

def q_company_stats(engine, metadata, symbol):
    company = Table('company', metadata, autoload=True)
    query = select(company.c.symbol, company.c.pe, company.c.bookvalue, company.c.divps, company.c.divyield, company.c.eps, company.c.analyst_price_target, company.c.price_to_book, company.c.beta, company.c.shares, company.c.divdate, company.c.exdivdate).\
    where(company.c.symbol == symbol)
    return query

def gainers(start, end, engine):

    stmt = text("select a.symbol, c.name, " + \
            "c.country, c.sector, c.industry, c.exchange, c.market_cap, " + \
            "a.close, " + \
            "b.close as last_close, " + \
            "((b.close-a.close)/((a.close+b.close)/2) * 100) as changepct " + \
            "from time_series_weekly_adjusted a  " + \
            "join time_series_weekly_adjusted b on a.symbol=b.symbol " + \
            "left join company c on a.symbol = c.symbol " + \
            "where a.week_ending = :start " + \
            "and b.week_ending = :week; ")

    stmt = stmt.bindparams(start=start, week=end)
    result = engine.execute(stmt)
    matches = []
    count=0
    # print(stmt)

    for symbol, name, country, sector, industry, exchange, market_cap, changepct, last_close in result.columns('symbol', 'name', 'country', 'sector', 'industry', 'exchange', 'market_cap','changepct', 'last_close'):
        # x  = {"symbol": symbol, "name": name, "average_close": average_close, "as_at": as_at}
        res = []
        res.append(symbol)
        res.append(name)
        res.append(country)
        res.append(sector)
        res.append(industry)
        res.append(exchange)
        res.append(market_cap)
        res.append(changepct)
        res.append(last_close)

        matches.append(res)
        count = count + 1

    return matches

def monthly_prices_from_weekly(symbol, engine, metadata, week_limit):
    current_date = datetime.now()
    delta = current_date - timedelta(weeks=week_limit)
    weekly = Table('time_series_weekly_adjusted', metadata, autoload=True)
    query = select(weekly.c.symbol, func.year(weekly.c.week_ending), func.month(weekly.c.week_ending), func.min(weekly.c.adjusted_close), func.max(weekly.c.adjusted_close)).\
    where(weekly.c.symbol == symbol).\
    where(weekly.c.week_ending > delta).\
    group_by(weekly.c.symbol, func.year(weekly.c.week_ending), func.month(weekly.c.week_ending))
    return query

def unique_sectors(engine, metadata):
    sector = Table('sector', metadata, autoload=True)
    query = select(sector.c.sector, sector.c.sectorid)
    query = query.distinct(sector.c.sector).order_by(sector.c.sector)
    return query

def q_unique_industries(engine, metadata, args=None):
    company = Table('company', metadata, autoload=True)
    query = select(company.c.industry)

    sector = args.get('sector','')
    if sector:
        query = query.where(company.c.sector == sector)

    industry = args.get('industry','')
    if industry:
        # query = query.where(company.c.industry == industry)
        cte = select(company.c.sector, company.c.industry).where(company.c.industry == industry).cte("foo")
        query = select(distinct(company.c.industry)).where(cte.c.sector == company.c.sector)

    query = query.distinct(company.c.industry).order_by(company.c.industry)
    return query

def industries_for_sector(engine, metadata, sector):
    company = Table('company', metadata, autoload=True)
    query = text("select distinct industry from company where sector = '" + sector + "'")
    return query

def q_rev_earnings(symbol, engine, metadata):
    income = Table('income_statement', metadata, autoload=True)
    query = select(income.c.symbol, income.c.fiscalDateEnding, income.c.totalRevenue, income.c.netIncome).\
    where(income.c.symbol == symbol).\
    order_by(income.c.fiscalDateEnding)
    return query

def q_debt(symbol, engine, metadata):
    bs = Table('balance_sheet', metadata, autoload=True)
    query = select(bs.c.symbol, bs.c.fiscalDateEnding, bs.c.totalNonCurrentLiabilities, bs.c.totalCurrentLiabilities, bs.c.commonStockSharesOutstanding).\
    where(bs.c.symbol == symbol).\
    order_by(bs.c.fiscalDateEnding)
    return query

def q_free_cashflow(symbol, engine, metadata):
    fcf = Table('fcf', metadata, Column("symbol"), Column("market_cap"), Column("fiscalDateEnding"),  Column("reportedCurrency"),  Column("operatingCashflow"),  Column("capitalExpenditures"),  Column("fcf_using_operating_cashflow"),  Column("cash_and_cash_equivalents"), extend_existing=True)
    query = select(fcf.c.symbol, fcf.c.market_cap, fcf.c.fiscalDateEnding, fcf.c.reportedCurrency, fcf.c.operatingCashflow, fcf.c.capitalExpenditures, fcf.c.fcf_using_operating_cashflow, fcf.c.cash_and_cash_equivalents).\
    where(fcf.c.symbol == symbol).\
    order_by(fcf.c.fiscalDateEnding.desc())
    return query

def q_weeklies(engine, metadata, symbol, no_of_weeks=None):
    weekly = Table('time_series_weekly_adjusted', metadata, autoload=True)
    company = Table('company', metadata, autoload=True)
    query = select(company.c.name, weekly.c.week_ending, weekly.c.adjusted_close).where(weekly.c.symbol == symbol).where(weekly.c.symbol == company.c.symbol)

    return query

def q_dailies(symbol, engine, metadata, no_of_days=None):
    daily = Table('time_series_daily', metadata, autoload=True)
    company = Table('company', metadata, autoload=True)
    query = select(company.c.name, daily.c.day_ending, daily.c.close).where(daily.c.symbol == symbol).where(daily.c.symbol == company.c.symbol)

    if no_of_days:
        current_date = datetime.now()
        days_int = int(no_of_days)
        delta = current_date - timedelta(days=days_int)
        query = query.where(daily.c.day_ending > delta)

    return query

def q_shares_outstanding(symbol, engine, metadata):
    balance_sheet = Table('balance_sheet', metadata, autoload=True)
    query = select(balance_sheet.c.fiscalDateEnding, func.coalesce(balance_sheet.c.commonStockSharesOutstanding, balance_sheet.c.commonStock).label('commonStockSharesOutstanding')).\
    where(balance_sheet.c.symbol == symbol).\
    order_by(balance_sheet.c.fiscalDateEnding.asc())
    # print(query)
    return query

def earnings_surprises(engine, metadata, start_date, end_date, args=None):
    current_date = datetime.now()
    earnings = Table('earnings', metadata, autoload=True)
    company = Table('company', metadata, autoload=True)
    company_country = Table('company_country', metadata, autoload=True)
    query = select(company.c.symbol, company.c.name, company_country.c.country, company.c.sector, company.c.industry, company.c.exchange, company.c.market_cap, earnings.c.fiscalDateEnding, earnings.c.reportedDate, earnings.c.reportedEPS, earnings.c.estimatedEPS, earnings.c.surprise, cast(earnings.c.surprisePercentage, Numeric(10,4))).\
    join(company_country, company.c.symbol == company_country.c.symbol, isouter=True).\
    join(earnings, company.c.symbol == earnings.c.symbol).\
    where(earnings.c.reportedDate >= start_date).\
    where(earnings.c.reportedDate <= end_date).\
    where(earnings.c.surprisePercentage is not None).\
    where(earnings.c.surprisePercentage != "None")
    # select_from(earnings.join(company, company.c.symbol == earnings.c.symbol))
    # order_by(earnings.c.symbol).order_by(earnings.c.reportedDate)

    query = apply_company_filters(query, company, args)
    offset = None
    offset_str = args.get('start')
    if offset_str:
        offset = int(offset_str)
    else:
        offset = 0

    sort_string = args.get('sort','')
    sort = None
    if sort_string:
        if sort_string == 'asc':
            sort = "asc"
            query = query.order_by(asc(cast(earnings.c.surprisePercentage, Numeric(10,4))))
        else:
            sort = "desc"
            query = query.order_by(desc(cast(earnings.c.surprisePercentage, Numeric(10,4))))

    return query, offset, sort

def q_historical_changepct(engine, metadata, start_date, end_date, args=None):
    company = Table('company', metadata, autoload=True)
    company_country = Table('company_country', metadata, autoload=True)
    weekly = Table('time_series_weekly_adjusted', metadata, autoload=True)

    historicals = select(weekly.c.symbol, func.avg(weekly.c.adjusted_close).label("avg_close"), func.min(weekly.c.adjusted_close).label("min_close"), func.max(weekly.c.adjusted_close).label("max_close")).\
        group_by(weekly.c.symbol).where(between(weekly.c.week_ending, start_date, end_date)).cte("historicals")

    currents = select(weekly.c.symbol, func.max(weekly.c.week_ending).label("latest_date")).group_by(weekly.c.symbol).cte("currents")

    query = select(company.c.symbol, company.c.name, company_country.c.country, company.c.sector, company.c.industry, company.c.market_cap, historicals.c.min_close, historicals.c.max_close, historicals.c.avg_close, currents.c.latest_date, weekly.c.adjusted_close, func.changepct(historicals.c.avg_close, weekly.c.adjusted_close).label("changepct")).\
        where(company.c.symbol == historicals.c.symbol).where(company_country.c.symbol==company.c.symbol).where(historicals.c.symbol == currents.c.symbol).where(weekly.c.symbol == currents.c.symbol).where(weekly.c.week_ending == currents.c.latest_date)

    offset = None
    offset_str = args.get('start')
    if offset_str:
        offset = int(offset_str)
    else:
        offset = 0

    sort_string = args.get('sort','')
    sort = None
    if sort_string:
        if sort_string == 'asc':
            sort = "asc"
            query = query.order_by(asc("changepct"))
        else:
            sort = "desc"
            query = query.order_by(desc("changepct"))

    return query, offset, sort

def q_price_changes(engine, metadata, start_date, end_date, filteropt=None, args=None):
    company = Table('company', metadata, autoload=True)
    weekly = Table('time_series_weekly_adjusted', metadata, autoload=True)
    company_country = Table('company_country', metadata, autoload=True)

    historicals = select(weekly.c.symbol, func.avg(weekly.c.adjusted_close).label("avg_close")).\
        group_by(weekly.c.symbol).where(between(weekly.c.week_ending, start_date, end_date)).cte("historicals")

    currents = select(weekly.c.symbol, func.max(weekly.c.week_ending).label("latest_date")).group_by(weekly.c.symbol).cte("currents")

    query = select(company.c.symbol, company.c.name, company_country.c.country, company.c.sector, company.c.industry, company.c.market_cap, historicals.c.avg_close, weekly.c.close, currents.c.latest_date, func.changepct(historicals.c.avg_close, weekly.c.adjusted_close).label("changepct")).\
        where(company.c.symbol == historicals.c.symbol).where(company_country.c.symbol==company.c.symbol).where(historicals.c.symbol == currents.c.symbol).where(weekly.c.symbol == currents.c.symbol).where(weekly.c.week_ending == currents.c.latest_date)

    if filteropt:
        if filteropt == 'gainers':
            query = query.where(weekly.c.close >= historicals.c.avg_close)
        if filteropt == 'decliners':
            query = query.where(weekly.c.close < historicals.c.avg_close)

    offset = None
    if args:
        offset_str = args.get('start','')
        if offset_str:
            offset = int(offset_str)
        else:
            offset = 0
        sort_string = args.get('sort','')
        sort = "desc"
        if sort_string:
            if sort_string == 'asc':
                sort = "asc"
                query = query.order_by(asc("changepct"))
            else:
                sort = "desc"
                query = query.order_by(desc("changepct"))

    return query, offset, sort

def q_market_cap_balance_sheet(engine, metadata, symbol):
    view = Table('market_cap_balance_sheet', metadata, autoload=True)
    query = select(view.c.symbol, view.c.market_cap, view.c.fiscaldateending, view.c.reportedcurrency, view.c.totalassets, view.c.cashAndCashEquivalentsAtCarryingValue, view.c.totalliabilities, view.c.longTermDebt).\
    where(view.c.symbol == symbol).order_by(view.c.fiscaldateending)
    return query

def q_market_cap_income_statement(engine, metadata, symbol):
    view = Table('market_cap_income_statement', metadata, autoload=True)
    query = select(view.c.symbol, view.c.market_cap, view.c.fiscaldateending, view.c.reportedcurrency, view.c.totalrevenue, view.c.costofrevenue, view.c.grossprofit, view.c.operatingincome,\
    view.c.sellinggeneralandadministrative, view.c.operatingexpenses, view.c.interestincome, view.c.netinterestincome, view.c.interestexpense, view.c.depreciationandamortization,\
    view.c.incomebeforetax, view.c.incometaxexpense, view.c.ebit, view.c.ebitda, view.c.netincome).\
    where(view.c.symbol == symbol).order_by(view.c.fiscaldateending)
    return query

def q_price_to_book(engine, metadata, args=None):
    view = Table('book_value_vs_price', metadata, autoload=True)
    query = select(view.c.symbol, view.c.name, view.c.country, view.c.sector, view.c.industry, view.c.market_cap, view.c.adjusted_close, view.c.bookvalue, view.c.week, func.changepct(view.c.bookvalue, view.c.adjusted_close).label("changepct"))
    query = query.where(view.c.bookvalue > view.c.adjusted_close)

    offset = None
    if args:
        offset_str = args.get('start','')
        if offset_str:
            offset = int(offset_str)
        else:
            offset = 0
        industry = args.get('industry', '')
        if industry:
            query = query.where(view.c.industry == industry)

        sector = args.get('sector', '')
        if sector:
            query = query.where(view.c.sector == sector)
    else:
        offset = 0

    sort_string = args.get('sort','')
    sort = "desc"
    if sort_string:
        if sort_string == 'asc':
            sort = "asc"
            query = query.order_by(asc("changepct"))
        else:
            sort = "desc"
            query = query.order_by(desc("changepct"))

    return query, offset, sort

def q_upcoming_earnings_calendar(engine, metadata):
    current_date = datetime.now()
    ecv = Table('earnings_calendar_view', metadata, autoload=True)
    query = select([col for col in ecv.columns]).where(ecv.c.report_date >= current_date).order_by(ecv.c.report_date, ecv.c.symbol)
    return query

def q_upcoming_earnings_calendar_min_max(engine, metadata):
    current_date = datetime.now()
    ecv = Table('earnings_calendar_view', metadata, autoload=True)
    q_min_max = select(func.min(ecv.c.report_date), func.max(ecv.c.report_date)).where(ecv.c.report_date >= current_date)
    return q_min_max


