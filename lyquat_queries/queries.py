from sqlalchemy import Table, select, func, between, or_

def q_historical_changepct(engine, metadata, start_date, end_date, args=None):
    company = Table('company', metadata, autoload=True)
    industry = Table('industry', metadata, autoload=True)
    weekly = Table('time_series_weekly_adjusted', metadata, autoload=True)

    historicals = select(weekly.c.symbol, func.avg(weekly.c.adjusted_close).label("avg_close"), func.min(weekly.c.adjusted_close).label("min_close"), func.max(weekly.c.adjusted_close).label("max_close")).\
        group_by(weekly.c.symbol).where(between(weekly.c.week_ending, start_date, end_date)).cte("historicals")

    currents = select(weekly.c.symbol, func.max(weekly.c.week_ending).label("latest_date")).group_by(weekly.c.symbol).cte("currents")

    query = select(company.c.symbol, company.c.name, company.c.market_cap, historicals.c.min_close, historicals.c.max_close, historicals.c.avg_close, weekly.c.adjusted_close, func.changepct(historicals.c.avg_close, weekly.c.adjusted_close).label("changepct"), industry.c.industryid, industry.c.industry, company.c.pe).\
        where(company.c.symbol == historicals.c.symbol).where(historicals.c.symbol == currents.c.symbol).where(weekly.c.symbol == currents.c.symbol).where(weekly.c.week_ending == currents.c.latest_date).\
        where(company.c.industry == industry.c.industry)

    return query
    
def q_search(engine, metadata, search):
    company = Table('company', metadata, autoload=True)
    query = select(company.c.symbol, company.c.name).where(or_(company.c.symbol.ilike(search + "%"), company.c.name.ilike(search + "%"))).limit(10)
    return query