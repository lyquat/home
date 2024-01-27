from flask_frozen import Freezer
import click
from sqlalchemy import create_engine, MetaData, Table, Column, String
from main import app, q_companies
from lyquat_queries import q_companies
from flask import url_for

app.config['FREEZER_SKIP_EXISTING'] = False
app.config['FREEZER_REMOVE_EXTRA_FILES'] = True
app.config['FREEZER_DESTINATION'] = '/home/notexists/build/'
freezer = Freezer(app)

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

with click.progressbar(
    freezer.freeze_yield(),
    item_show_func=lambda p: p.url if p else 'Done!') as urls:
    for url in urls:
    # everything is already happening, just pass
        pass

# if __name__ == '__main__':
#     freezer.freeze()

