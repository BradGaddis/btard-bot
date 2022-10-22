import csv
from dataclasses import field
from alpaca.trading.client import TradingClient
import assetpicker
from config import *
import pandas as pd
import asyncio as asy
import yfinance as yf
import time
import concurrent.futures
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os


class stock_trader():
    def __init__(self, key = ALPACA_PAPER_KEY, skey = ALPACA_PAPER_SECRET_KEY) -> None:
        """Trading object: Instanciates to paper account by default, unless specified otherwise."""
        self.trading_client = TradingClient(key, skey)
        self.positions = self.trading_client.get_all_positions()
        self.pos_keys = [pos[0] for pos in self.positions[0]]
        self.pos_values = []    

        trading_client = TradingClient(api_key=key,secret_key=skey)
        self.buying_power = float(trading_client.get_account().non_marginable_buying_power)
        self.gamblin_money = self.buying_power * .01 if self.buying_power > 1 else 1    
        self.long_term_invest_amount = (self.buying_power - self.gamblin_money) * .9
        
        for i , pos in enumerate(self.positions):
            self.pos_values.append([])
            for tup in pos:
                self.pos_values[i].append((tup[1]))

        pos_df = pd.DataFrame(self.pos_values, columns=self.pos_keys)
        pos_df = pos_df.iloc[:,1:]

    def get_position_df(self):
        """Returns a dataframe of the current positions held in portfolio"""
        pos_df = pd.DataFrame(self.pos_values, columns=self.pos_keys)
        pos_df = pos_df.iloc[:,1:]
        return pos_df
        

    def find_potential_new_pos(self):
        pass

    def get_position_tickers(self):
        return [asset.symbol for asset in self.positions]

    # def get_position_financials(self):
    #     for stock in self.get_position_tickers():
    #         print(stock, assetpicker.check_stock_financial(stock), "\n_________________________\n")


    def set_gambling_params(self, total_amount = 0):
        #check if params already set
        if os.path.exists('portfolio_params.csv'):
            with open ("portfolio_params.csv", "r") as params_txt:
                reader = csv.reader(params_txt)
                for row in reader:
                    print(row)
        else :
            # set the params
            Crypto_gambling_amout = 0

            params = ["Crypto_gambling_amout"]
            with open ("portfolio_params.csv", "w") as params_txt:
                writer = csv.DictWriter(params_txt, fieldnames=params)
                writer.writeheader()
                writer.writerow(dict({"Crypto_gambling_amout": {Crypto_gambling_amout}}))
                
    def run(self):
        cur_positions = self.get_position_tickers()
        # Show current held positions
        print(f"You are currently holding: {cur_positions}")
        # time.sleep(3)
        # print(f"Here are the financials for the stock that you own:")
        # self.get_position_financials()
        # print("Checkout these stocks:")
        self.set_gambling_params()