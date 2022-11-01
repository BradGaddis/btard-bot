import requests
import json
from config import *
import csv
import yfinance as yf
import time
import pandas as pd
from datetime import date, datetime

def get_metrics():
    """Returns a list of criteria to search by"""
    metrics = []
    path = os.path.join(DATA_PATH, "yahooinfometrics.csv")
    with open(path, "r") as f:
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
    with open("./data/tradable_stocks.csv", "w") as f:
        write = csv.writer(f).writerow(output)
    return output
        

def check_metric_financial(stocks = []):
    pass

def compare_sectors(assets = []):

    pass

def check_stock_financial(stock="msft"):
    return yf.Ticker(stock).financials

def check_stock_info(stock):
    return yf.Ticker(stock).info


def get_interesting_stocks(market_cap = 3000000000, restart = False):
    """Prints a dataframe of stocks worth looking into by some arbitrary metrics. Market Cap < 3b by default"""

    # This method should be run Sunday-Friday after market close
    
    stocks_list = []
    try:
        with open("./data/tradable_stocks.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                stocks_list.append(row)
    except Exception:
        print(Exception)

    stocks_of_interest = []
    
    saved, complete = load_interesting_stocks(stocks_of_interest)
    
    if complete:
        return

    full_count = len(stocks_list[0])
    # print("continuing csv dict. remove it and start over? y/n") # TODO

    start_point = 0

    def write_interesting_csv(market_cap, stocks_list, stocks_of_interest, saved = {}, restart = False, full_count = 0 ):
        with open("./data/stocks_of_interest.csv", "w") as f:
            fields= ["ticker", *get_metrics(), "cash to debt","complete","lastCheck"]
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=',') 
            writer.writeheader()
            if not restart:
                for row in saved:
                    writer.writerow(row)

            for i, stock in enumerate(stocks_list[0]):
                cash_to_debt = ""
                clear = True
                nonlocal start_point 
                start_point += 1
                if stock in stocks_of_interest:
                    continue
                info = check_stock_info(stock)
                try: 
                    cash_to_debt = info["totalCash"] - info["totalDebt"] 
                except Exception as e:
                    print ("\033[A                                                                         \033[A")
                    print("exception: ", e)
                    continue
                else:
                    try:
                        if info["country"] == "United States" and cash_to_debt > 0 and info["dividendYield"] and info["marketCap"] <= market_cap and info["beta"] < 1:
                            stocks_of_interest.append(stock)
                            row = dict({"ticker": str(stock)})
                            for metric in get_metrics():
                                try:
                                    row[str(metric)] = str(info[metric])
                                except:
                                    row[str(metric)] = None
                            row["cash to debt"] = str(cash_to_debt)
                            writer.writerow(row)
                            
                            clear = False
                            show_interesting_stock(stocks_of_interest, stock, cash_to_debt, info)
                        else: 
                            if clear:
                                print ("\033[A                             \033[A")
                            print(f"checking stock {start_point} of {full_count}, cash - debt:")
                            clear = True
                            
                    except Exception as e:
                        print ("\033[A                                                                         \033[A")
                        print("error: ", e)
                        
            writer.writerow({"complete" : True, "lastCheck" : datetime.now()})


    has_started = False
    while not complete:
        try:
            print(f"stocks of interest {stocks_of_interest}")
            if not has_started:
                if len(stocks_of_interest) == 0:
                    start_point = 0 
                else:
                    start_point = stocks_list[0].index(stocks_of_interest[-1])
            try:
                stocks_list[0] = stocks_list[0][start_point :]
                start_point = full_count - len(stocks_list[0])
            except Exception as e:
                print("inner loop error: ",e)

                print(f"start point: {start_point}")    
                if start_point == 0:
                    restart = True
            has_started = True
            # check stocks that have a positive cash to debt ratio
            write_interesting_csv(market_cap, stocks_list, stocks_of_interest, saved, restart = restart, full_count= full_count)
        except Exception as e:
            print("attempting to wait it out...",e)
            time.sleep(5)

def load_interesting_stocks(stocks_of_interest, path= "./data/stocks_of_interest.csv"):
    saved = []
    complete = False
    try:
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                saved.append(row)
                if row["complete"]:
                    # print("You have the full list")
                    complete = True
                    break
                stocks_of_interest.append(row["ticker"])
                # print(row["ticker"])
    
    except Exception as e:
        print(e)
    return saved, complete




def show_interesting_stock(stocks_of_interest, stock, cash_to_debt, info):
    print(stock, [(metric, info[metric]) for metric in get_metrics()],("cash to debt",cash_to_debt),"\n",info["longBusinessSummary"], "\n",stocks_of_interest,"\n", len(stocks_of_interest),"\n")


def interesting_csv_to_df():
    stocks_list = []
    try:
        with open("./data/tradable_stocks.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                stocks_list.append(row)
    except Exception:
        print(Exception)

    stocks = load_interesting_stocks(stocks_list)
    # print(stocks[0])
    df = pd.DataFrame.from_dict(stocks[0])

    return df

# check stocks that have revenue that is growing

# interesting_csv_to_df()

# get_interesting_stocks()

def get_info_all():
    stocks_list = []
    try:
        with open(os.path.join(DATA_PATH,"all_tradable_stocks_info.csv"), "r") as f:
            reader = csv.reader(f)
            for row in reader:
                stocks_list.append(row)
    except Exception:
        print(Exception)

    stocks_of_interest = []
    
    saved, complete = load_interesting_stocks(stocks_of_interest, os.path.join(DATA_PATH,"all_tradable_stocks_info.csv"))
    
    if complete:
        return
