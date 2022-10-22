import assetpicker as ap
from config import *
import os
import concurrent.futures
from stocktrader import trader_agent

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     executor.map()

# get csv of all stocks in nyse
# get name of all crypto assets traded on alpaca
st = trader_agent()

def main():
    st.run()
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     pass


if __name__ == "__main__":
    main()

