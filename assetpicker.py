from stockinfo import *
import requests
import json
from config import *
import csv
import yfinance as yf

def get_metrics():
    """Returns a list of criteria to search by"""
    metrics = []
    with open("yahooinfometrics.csv", "r") as f:
        reader = csv.reader(f)
        metrics = list(reader)

    for i in range(len(metrics[0])):
        metrics[0][i] = metrics[0][i].strip()
    return metrics[0]


def get_tradable_stocks():
    """Returns a list of stocks supported on alpaca, writes a csv file"""
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
    return output
        


    
    
        

def check_metric_financial(stocks = []):
    # total revenue should be increasing on average on avereage
    # gross profit should be increasing every year on avereage
    # income before tax should increase on average
    # should be below 200 ma 
    # ratio of cash to debt should be positive
    # check rsi
    # check macd?
    # compare sectors?
    pass

def compare_sectors(assets = []):

    pass








def check_stock_financial(stock="msft"):
    return yf.Ticker(stock).financials

def check_balance_sheet(asset = "SPY"): 
    for i in range(len(asset)):
        check_stock(asset[0])

def check_stock_info(stock):
    return yf.Ticker(stock).info


def print_interesting_stocks(market_cap = None):
    """Prints a datafram of stocks worth looking into by some arbitray metrics"""
    stocks_list = []
    try:
        with open("tradable_stocks.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                stocks_list.append(row)
    except:
        stocks_list = get_tradable_stocks()

    stocks_of_interest = []
    
    
    # print(stocks_list[0][1])
    # check stocks that have a positive cash to debt ratio
    with open("stocks_of_interest.csv", "w") as f:
        fields= ["ticker", *get_metrics(), "cash to debt", "longBusinessSummary"]
        writer = csv.DictWriter(f, fieldnames=fields) 
        writer.writeheader()
    
        for stock in stocks_list[0]:
            cash_to_debt = ""
            try: 
                cash_to_debt = check_stock_info(stock)["totalCash"] - check_stock_info(stock)["totalDebt"] 
            except:
                continue
            else:
                try:
                    if check_stock_info(stock)["country"] == "United States" and cash_to_debt > 0:
                        stocks_of_interest.append(stock)
                        info = check_stock_info(stock)

                        writer.writerow({"ticker": str(stock)})
                        for metric in get_metrics():
                            try:
                                writer.writerow({str(metric): str(info[metric])})
                            except:
                                writer.writerow({str(metric): "None"})
                        writer.writerow({"cash to debt": str(cash_to_debt)})
                        writer.writerow({"longBusinessSummary": str(info["longBusinessSummary"])})


                        print(stock, [(metric, info[metric]) for metric in get_metrics()],("cash to debt",cash_to_debt),"\n",info["longBusinessSummary"], "\n",stocks_of_interest,"\n", len(stocks_of_interest),"\n")
                except:
                    pass

    # print(check_stock_info(stocks_list[0][1]))
    # check stocks that have revenue that is growing



print_interesting_stocks()