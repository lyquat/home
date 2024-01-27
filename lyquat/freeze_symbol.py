import click
from flask_frozen import Freezer
from main import app, q_companies
from sqlalchemy import create_engine, MetaData, Table, Column, String
from flask import url_for
import sys
#from warnings import simplefilter as filter_warnings
import warnings

warnings.filterwarnings('ignore')

# DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='reader', password='password', server='localhost', database='dev_lyquat')
# engine = create_engine(DATABSE_URI)
# metadata = MetaData(bind=engine, schema="dev_lyquat")

app.config['FREEZER_SKIP_EXISTING'] = False
app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
app.config['FREEZER_STATIC_IGNORE'] = ['*']
app.config['FREEZER_DESTINATION'] = '/home/build/'
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True
freezer = Freezer(app, with_no_argument_rules=False, log_url_for=False)
# freezer = Freezer(app)

args = sys.argv
foo = args[1]

@freezer.register_generator
def symbol():
    yield url_for('symbol', symbol=foo)

@freezer.register_generator
def js():
    yield url_for('js', symbol=foo)

#         freezer.freeze_yield(),
#         item_show_func=lambda p: p.url if p else 'Done!') as urls:
#     for url in urls:
#         # everything is already happening, just pass
#         pass

if __name__ == '__main__':
    freezer.freeze()
