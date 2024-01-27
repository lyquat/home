import sys
import datetime
import yfinance as yf
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text, insert, delete, update

def build(city, state, country, website, recommendationKey, numberOfAnalystOpinions, targetLowPrice, targetMedianPrice, targetHighPrice, logo_url):
	values = {"city": city, "state": state, "country": country, "website": website, "recommendationKey": recommendationKey, "numberOfAnalystOpinions": numberOfAnalystOpinions, "targetLowPrice": targetLowPrice, "targetMedianPrice": targetMedianPrice, "targetHighPrice": targetHighPrice, "logo_url": logo_url}
	return values

DATABSE_URI='mysql+mysqldb://{user}:{password}@{server}/{database}'.format(user='XXXXX', password='XXXXX_password', server='localhost', database='XXXXX')
engine = create_engine(DATABSE_URI)
metadata = MetaData(bind=engine, schema="XXXXX")

args = sys.argv
symbol = None

if len(args) != 2:
	exit("ERROR: No symbol supplied")

symbol = args[1]

ticker = yf.Ticker(symbol)
info = ticker.info
print(info)

city = info['city'] if 'city' in info else None
state = info['state'] if 'state' in info else None
country = info['country'] if 'country' in info else None
website = info['website'] if 'website' in info else None
recommendationKey = info['recommendationKey'] if 'recommendationKey' in info else None
numberOfAnalystOpinions = info['numberOfAnalystOpinions'] if 'numberOfAnalystOpinions' in info else None
targetLowPrice = info['targetLowPrice'] if 'targetLowPrice' in info else None
targetMedianPrice = info['targetMedianPrice'] if 'targetMedianPrice' in info else None
targetHighPrice = info['targetHighPrice'] if 'targetHighPrice' in info else None
logo_url = info['logo_url'] if 'logo_url' in info else None

data = build(city, state, country, website, recommendationKey, numberOfAnalystOpinions, targetLowPrice, targetMedianPrice, targetHighPrice, logo_url)

#print(data)
exit()

company_supplementary = Table('company_supplementary', metadata, autoload_with=engine)
query = select(company_supplementary.c.symbol).where(company_supplementary.c.symbol == symbol)
exists = engine.execute(query).first() is not None

if exists:
	s = {"symbol": symbol}
	s.update(data)
	statement = company_supplementary.update().where(company_supplementary.c.symbol == symbol).values(s)
	result = engine.execute(statement)
else:
	s = {"symbol": symbol}
	s.update(data)
	statement = insert(company_supplementary, s)
	result = engine.execute(statement)


