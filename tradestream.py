from alpaca.trading.stream import TradingStream
from config import *

# this module handles information about trades and stuff we make?

trading_stream = TradingStream(ALPACA_PAPER_KEY, ALPACA_PAPER_SECRET_KEY, paper=True)

output_data = {}


async def update_handler(data):
    # trade updates will arrive in our async handler
    output_data = data

    print(output_data)

    # TODO 
        # log this data to dataframe and save to csv

# subscribe to trade updates and supply the handler as a parameter
trading_stream.subscribe_trade_updates(update_handler)

# start our websocket streaming
trading_stream.run()
