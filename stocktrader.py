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



class stock_trader():
    def __init__(self, key = ALPACA_PAPER_KEY, skey = ALPACA_PAPER_SECRET_KEY) -> None:
        """Trading object: Instanciates to paper account by default, unless specified otherwise."""
        self.trading_client = TradingClient(key, skey)
        self.positions = self.trading_client.get_all_positions()
        self.pos_keys = [pos[0] for pos in self.positions[0]]
        self.pos_values = []    

        trading_client = TradingClient(api_key=key,secret_key=skey)
        self.buying_power = trading_client.get_account().non_marginable_buying_power
        self.play_month = self.buying_power * .01 if self.buying_power > 1 else 1

        print(self.buying_power)

        i = 0
        for pos in self.positions:
            self.pos_values.append([])
            for tup in pos:
                self.pos_values[i].append((tup[1]))
            i += 1

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

    def get_position_financials(self):
        for stock in self.get_position_tickers():
            print(stock, assetpicker.check_stock_financial(stock), "\n_________________________\n")
            

    def run(self):
        cur_positions = self.get_position_tickers()
        # Show current held positions
        print(f"You are currently holding: {cur_positions}")
        # time.sleep(3)
        # print(f"Here are the financials for the stock that you own:")
        # self.get_position_financials()
        # print("Checkout these stocks:")
        