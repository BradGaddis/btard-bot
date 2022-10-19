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
        


def check_stock_financial(stock="msft"):
    return yf.Ticker(stock).financials

def check_balance_sheet(asset = "SPY"): 
    for i in range(len(asset)):
        check_stock(asset[0])

