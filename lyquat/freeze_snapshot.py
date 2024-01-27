import click
from flask_frozen import Freezer
from main import app, q_companies
from sqlalchemy import create_engine, MetaData, Table, Column, String, select
from flask import url_for
import sys
from datetime import datetime

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

app.config['FREEZER_SKIP_EXISTING'] = False
app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
app.config['FREEZER_STATIC_IGNORE'] = ['*']
app.config['FREEZER_DESTINATION'] = '/home/build/'
freezer = Freezer(app, with_no_argument_rules=False, log_url_for=False)
# freezer = Freezer(app)

@freezer.register_generator
def index():
    yield url_for('index')
    
@freezer.register_generator
def calendar():
    yield url_for('calendar')

@freezer.register_generator
def snapshot_by_sector():
    sector = Table('sector', metadata, autoload=True)
    query = select(sector.c.sectorid)
    result = engine.execute(query)
    for row in result:
        sectorid = row[0]
        yield url_for('snapshot_by_sector', sectorid=sectorid)

@freezer.register_generator
def list_industry():
    industry = Table('company_sector_industry', metadata, autoload=True)
    query = select(industry.c.industryid.distinct())
    result = engine.execute(query)
    for row in result:
        industryid = row[0]
        yield url_for('list_industry', industry=industryid)
        
@freezer.register_generator
def js():
    industry = Table('company_sector_industry', metadata, autoload=True)
    query = select(industry.c.industryid.distinct())
    result = engine.execute(query)
    for row in result:
        industryid = row[0]
        yield url_for('js_list', industry=industryid)

now = datetime.now()
print("Starting..." + str(now))

with click.progressbar(
        freezer.freeze_yield(),
        item_show_func=lambda p: p.url if p else 'Done!') as urls:
    for url in urls:
        # everything is already happening, just pass
        pass

then = datetime.now()
duration = then - now
mins = divmod(duration.total_seconds(), 60)[0]
print("Done in " + str(mins) + " minutes")
