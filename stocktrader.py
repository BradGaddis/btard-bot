from alpaca.trading.client import TradingClient
from config import *
import pandas as pd
import asyncio as asy
import yfinance as yf

class stock_trader():
    def __init__(self, key = ALPACA_PAPER_KEY, skey = ALPACA_PAPER_SECRET_KEY) -> None:
        self.trading_client = TradingClient(key, skey)
        self.positions = self.trading_client.get_all_positions()
        self.pos_keys = [pos[0] for pos in self.positions[0]]
        self.pos_values = []
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

    def run(self):
        pass