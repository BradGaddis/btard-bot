import requests
from dotenv import load_dotenv
import assetpicker as ap
import os

# get csv of all stocks in nyse
# get name of all crypto assets traded on alpaca
load_dotenv()


def run():
    ap.get_assets()
    ap.check_balance_sheet()

if __name__ == '__main__':
    run()

# train the trades on a reinforcement model

