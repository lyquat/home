from datetime import datetime, timedelta
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import redirect
from flask import jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.sql import select
from queries import q_historical_changepct
from queries import q_search
from filters import human_format
from filters import color
from filters import format_2dp

app = Flask(__name__)

app.jinja_env.filters.update(human_format = human_format)
app.jinja_env.filters.update(color = color)
app.jinja_env.filters.update(format_2dp = format_2dp)

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

@app.route("/")
def index():
    return redirect(url_for('price_history'))

@app.route("/about")
def about():
    return redirect("http://lyquat.com/about")

@app.route("/<symbol>")
def symbol(symbol):
    return redirect("http://lyquat.com/" + symbol)

@app.route("/list/<industry>")
def industry(industry):
    return redirect("http://lyquat.com/list/" + industry)

@app.route("/price_history")
def price_history():
    if len(request.args) > 0:
        try:
            start_arg = request.args.get('start')
            end_arg = request.args.get('end')
            offset_arg = request.args.get('offset') or 0
            limit_arg = request.args.get('limit') or 100
            f = "%Y-%m-%d"
            start = datetime.strptime(start_arg, f)
            end = datetime.strptime(end_arg, f)
            query = q_historical_changepct(engine, metadata, start, end)
            offset = None
            limit = None
            if offset_arg != 0:
                try:
                    offset = int(offset_arg)
                    query = query.offset(offset)
                except:
                    offset = 0
            else:
                offset = 0
            if limit_arg !=100:
                try:
                    limit = int(limit_arg)
                    if limit != 0:
                        query = query.limit(limit)
                except:
                    limit = 100
                    query = query.limit(limit)
            else:
                limit = 100
                query = query.limit(limit)
            result = engine.execute(query)
            rows = []
            for row in result:
                x = {"symbol": row[0], "name": row[1], "market_cap": row[2], "min_close": row[3], "max_close": row[4],"avg_close": row[5], "last_close": row[6], "changepct": row[7], "industry_id": row[8], "industry": row[9], "pe": row[10]}
                rows.append(x)
            return render_template('price_history.html', rows=rows, start=start_arg, end=end_arg, offset=offset, limit=limit)
        except Exception as e:
            print(e)
            return render_template('price_history.html', rows=None, offset=0, limit=100)
    else:
        return render_template('price_history.html', rows=None, offset=0, limit=100)

@app.route("/search")
def search():
    
    q = request.args.get('q')
    query = q_search(engine, metadata, q)
    matches = []
    result = engine.execute(query)
    # return redirect(url_for('price_history'))
    for row in result:
        print(row)
        x = {"symbol": row[0], "name": row[1], "url": url_for('symbol',symbol=row[0])}
        matches.append(x)

    return jsonify(matches)

