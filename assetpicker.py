import webscraper
from stockinfo import *
import requests
import json
from config import *
import csv

def get_tradable_stocks():
    url = 'https://api.alpaca.markets/v2/assets?asset_class=us_equity'
    
    r = requests.get(url, headers={'Apca-Api-Key-Id': ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':ALPACA_LIVE_SECRET_KEY})
    obj = r.content
    output = []
    data = json.loads(obj)
    for stock in data:
        if stock["tradable"]:
            output.append(stock["symbol"])
    with open("tradable_stocks.csv", "w") as f:
        write = csv.writer(f).writerow(output)
    print(len(output))
    return output
        

def check_metric_financial():
    # total revenue should be increasing on average on avereage
    # gross profit should be increasing every year on avereage
    # income before tax should increase on average
    # should be below 200 ma 
    # check macd?
    
    pass

metrics = []
with open("yahooinfometrics.csv", "r") as f:
    reader = csv.reader(f)
    metrics = list(reader)

for i in range(len(metrics[0])):
    metrics[0][i] = metrics[0][i].strip()


def check_stock_financial(stock="msft"):
    return yf.Ticker(stock).financials

def check_balance_sheet(asset = "SPY"): 
    for i in range(len(asset)):
        check_stock(asset[0])

