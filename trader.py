import csv
from dataclasses import field
from datetime import datetime
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
from alpaca.trading.models import Calendar
import os
import requests
import json
# trading_client = TradingClient(ALPACA_PAPER_KEY, ALPACA_PAPER_SECRET_KEY)

# print(trading_client.get_clock().next_close)



class trader_agent():
    def __init__(self, key = ALPACA_PAPER_KEY, skey = ALPACA_PAPER_SECRET_KEY, paper = True) -> None:
        """Trading object: Instanciates to paper account by default, unless specified otherwise."""
        self.trading_client = TradingClient(key, skey)
        
        # this sets up an array of positons that are currently in the account
        self.positions = self.trading_client.get_all_positions()
        self.pos_keys = [pos[0] for pos in self.positions[0]]
        self.pos_values = []    

        # sets up how much money is in the account, how much you can gamble with crypto \
        # how much you can gamble on stocks
        # should move all of this into method
        # self.account_balance = float(self.trading_client.get_account().)
        
        # 10% remains in cash for manual buying 
        self.buying_power = float(self.trading_client.get_account().non_marginable_buying_power)
        self.gamblin_monty = self.buying_power * .01 if self.buying_power > 1 else 1    
        self.crypto_gameblin_monty = self.buying_power * .01 if self.buying_power > 1 else 1    
        self.long_term_invest_amount = (self.buying_power - self.gamblin_monty - self.crypto_gameblin_monty) * .9
        self.total_positions_allowed = 29
        
        self.check_set_gambling_params()
        for i , pos in enumerate(self.positions):
            self.pos_values.append([])
            for tup in pos:
                self.pos_values[i].append((tup[1]))

            pos_df = pd.DataFrame(self.pos_values, columns=self.pos_keys)
        pos_df = pos_df.iloc[:,1:]

    # I'm noob and couldn't figure out how to call the damn get_clock() method. Perhaps someone smarter than me can...
    def check_market_time(self):
        r = requests.get(LIVE_END_POINT + "/v2/clock", headers={"APCA-API-KEY-ID": ALPACA_LIVE_KEY, "APCA-API-SECRET-KEY": ALPACA_LIVE_SECRET_KEY})
        obj = r.content
        new_json = obj.decode('utf8').replace("'", '"')
        data = json.loads(new_json)
        print(data)

    def get_positions_df(self):
        """Returns a dataframe of the current positions held in portfolio"""
        pos_df = pd.DataFrame(self.pos_values, columns=self.pos_keys)
        pos_df = pos_df.iloc[:,1:]
        return pos_df
    
    def cancel_all_orders(self):
        self.trading_client.cancel_orders()

    def buy_position(self, ticker, amt, tif):
        # preparing orders
        notation_or_qty = "qty" # TODO
        market_order_data = MarketOrderRequest(
                            symbol=ticker,
                            notation_or_qty=amt,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.DAY
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

    def sell_position(self, ticker, amt, tif):
        # preparing orders
        notation_or_qty = "qty" # TODO
        market_order_data = MarketOrderRequest(
                            symbol=ticker,
                            notation_or_qty=amt,
                            side=OrderSide.SELL,
                            time_in_force=tif
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )


    def get_positions(self):
        for position in self.positions:
            print(position)
        return self.positions
    

    def get_position():
        pass

    def find_potential_new_pos(self):
        pass

    def get_position_tickers(self):
        return [asset.symbol for asset in self.positions]

    # def get_position_financials(self):
    #     for stock in self.get_position_tickers():
    #         print(stock, assetpicker.check_stock_financial(stock), "\n_________________________\n")

    def check_set_gambling_params(self):
        #check if params already set
        if os.path.exists(os.path.join(DATA_PATH ,'portfolio_params.csv')):
            with open (os.path.join(DATA_PATH,"portfolio_params.csv"), "r") as params_txt:
                reader = csv.reader(params_txt)
                for row in reader:
                    print(row)

            self.gamblin_monty = self.buying_power * .01 if self.buying_power > 1 else 1    
            self.crypto_gameblin_monty = 0
            self.long_term_invest_amount = (self.buying_power - self.gamblin_monty) * .9
        
        else :
            # set the params if they don't exist
            params = ["gamblin_monty","crypto_gameblin_monty","long_term_invest_amount"]
            with open (os.path.join(DATA_PATH ,"portfolio_params.csv"), "w") as params_txt:
                writer = csv.DictWriter(params_txt, fieldnames=params)
                writer.writeheader()
                writer.writerow(dict({"gamblin_monty": {self.gamblin_monty}}))
                writer.writerow(dict({"crypto_gameblin_monty": {self.crypto_gameblin_monty}}))
                writer.writerow(dict({"long_term_invest_amount": {self.long_term_invest_amount}}))
                
    def run(self):
        print(self.get_positions_df())