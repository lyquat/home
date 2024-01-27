import sys
import random
import csv
import requests
import mysql.connector
from datetime import date
from datetime import datetime
from datetime import timedelta

MAX_WEEKS = 52*10 # 10 years

# def getRandomKey():
#     path = 'api_keys3.txt'
#     keys = []
#     key = ''
#     with open(path, 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             keys.append(row)      
#         file.close()
#         key = random.choice(keys)[0]
#     return key

route = None
symbol = None

args = sys.argv
if len(args) == 3:
    route = args[1]
    symbol = args[2]
else:
    exit("ERROR: No symbol or route supplied in " + sys.argv[0])

url = 'XXXXX.amazonaws.com/e' + str(route) + '?symbol=' + symbol

cnx = mysql.connector.connect(user='XXXXX', password='XXXXX_password', database='XXXXX')
cursor = cnx.cursor()

response = requests.get(url, timeout=20)

json_data = response.json() if response and response.status_code == 200 else None

current_datetime = str(date.today())

cursor.execute("delete from earnings where symbol= '" + symbol + "';")

add_earnings = ("INSERT INTO earnings "
               "(symbol, fiscalDateEnding, reportedDate, reportedEPS, estimatedEPS, surprise, surprisePercentage) "
               "VALUES (%(symbol)s, %(fiscalDateEnding)s, %(reportedDate)s, %(reportedEPS)s, %(estimatedEPS)s, %(surprise)s, %(surprisePercentage)s)")

if json_data and 'quarterlyEarnings' in json_data:
    symbol = json_data['symbol']
    earnings = json_data['quarterlyEarnings']
    now = datetime.now()
    for e in earnings:
        quarter = datetime.strptime(e['fiscalDateEnding'], '%Y-%m-%d')
        delta = now - timedelta(weeks=MAX_WEEKS)
        if(quarter < delta):
            continue
        earnings_data = {
            'symbol': symbol,
            'fiscalDateEnding': e['fiscalDateEnding'],
            'reportedDate': e['reportedDate'],
            'reportedEPS': e['reportedEPS'],
            'estimatedEPS': e['estimatedEPS'],
            'surprise': e['surprise'],
            'surprisePercentage': e['surprisePercentage']
        }
        cursor.execute(add_earnings, earnings_data)
elif json_data and 'Invalid API call' in json_data:
    print("   ---> invalid API call")
    exit()
elif json_data and ('Information' in json_data or 'Note' in json_data):
    print("   ---> Rate limited")
    exit(1)
elif json_data == None:
    print("   ---> null response object: " + str(response))
    exit()
elif len(json_data) == 0:
    print("   ---> no data found in response")
    exit()
else:
    print("   ---> data: " + str(json_data))
    exit()

cnx.commit()
cursor.close()
cnx.close()
