from inspect import cleandoc
from logging import exception
from stockinfo import *
import requests
import json
from config import *
import csv
import yfinance as yf
import time
import pandas as pd


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


def print_interesting_longterm_stocks(market_cap = 3000000000, restart = False):
    """Prints a dataframe of stocks worth looking into by some arbitrary metrics. Market Cap < 3b by default"""
    stocks_list = []
    try:
        with open("tradable_stocks.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                stocks_list.append(row)
    except Exception:
        print(Exception)
    #     stocks_list = get_tradable_stocks()

    stocks_of_interest = []
    # import pandas as pd
    # stocks_of_interest = pd.read_csv('stocks_of_interest.csv', header=None, index_col=0, squeeze=True).to_dict()

    
    # check stocks that have a positive cash to debt ratio
    saved = []
    saved_dict = {}
    try:
        with open('stocks_of_interest.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                saved.append(row)
                stocks_of_interest.append(row["ticker"])
                print(row["ticker"])

    except Exception as e:
        print(e)

        # pass

     
    # print("continuing csv dict. remove it and start over? y/n") # TODO
    
    print(f"stocks of interest {stocks_of_interest}")

    if len(stocks_of_interest) == 0:
        start_point = 0 
    else:
        start_point = stocks_list[0].index(stocks_of_interest[-1])  + 1
    
    stocks_list[0] = stocks_list[0][start_point :]

    print(f"start point: {start_point}")    
    if start_point == 0:
        restart = True
    
    if 
    write_interesting_csv(market_cap, stocks_list, f, stocks_of_interest, saved, restart = restart)

def write_interesting_csv(market_cap, stocks_list, f, stocks_of_interest, saved = {}, restart = False ):
    with open("stocks_of_interest.csv", "w") as f:
        fields= ["ticker", *get_metrics(), "cash to debt","complete"]
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=',') 
        writer.writeheader()
        if not restart:
            for row in saved:
                writer.writerow(row)


        for i, stock in enumerate(stocks_list[0]):
            cash_to_debt = ""
            # time.sleep(.05)
            clear = True
            info = check_stock_info(stock)
            try: 
                cash_to_debt = info["totalCash"] - info["totalDebt"] 
            except:
                continue
            else:
                try:
                    if info["country"] == "United States" and cash_to_debt > 0 and info["dividendYield"] and info["marketCap"] <= market_cap and info["beta"] < 1:
                        stocks_of_interest.append(stock)
                        row = dict({"ticker": str(stock)})
                        # writer.writerow({"ticker": str(stock)})
                        for metric in get_metrics():
                            try:
                                row[str(metric)] = str(info[metric])
                                # writer.writerow({str(metric): str(info[metric])})
                            except:
                                 row[str(metric)] = None
                                # writer.writerow({str(metric): "None"})
                        row["cash to debt"] = str(cash_to_debt)
                        # print(row)
                        # writer.writerow({"cash to debt": str(cash_to_debt)})
                        writer.writerow(row)
                        
                        clear = False
                        show_interesting_stock(stocks_of_interest, stock, cash_to_debt, info)
                    else: 
                        if clear:
                            print ("\033[A                             \033[A")
                        print(f"checking stock {i} of {len(stocks_list[0])}")
                        clear = True
                        
                except Exception as e:
                    print("error: ", e)
        writer.writerow({"complete" : True})

def show_interesting_stock(stocks_of_interest, stock, cash_to_debt, info):
    print(stock, [(metric, info[metric]) for metric in get_metrics()],("cash to debt",cash_to_debt),"\n",info["longBusinessSummary"], "\n",stocks_of_interest,"\n", len(stocks_of_interest),"\n")

    # print(check_stock_info(stocks_list[0][1]))
    # check stocks that have revenue that is growing



print_interesting_longterm_stocks()