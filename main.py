import assetpicker as ap
from config import *
import os

from stocktrader import stock_trader

# get csv of all stocks in nyse
# get name of all crypto assets traded on alpaca


def run():
    ap.get_assets()
    ap.check_balance_sheet()

if __name__ == '__main__':
    stock_trader = stock_trader(ALPACA_PAPER_KEY, ALPACA_PAPER_SECRET_KEY)
    stock_trader.run()

# train the trades on a reinforcement model

