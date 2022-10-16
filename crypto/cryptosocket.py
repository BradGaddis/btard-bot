from config import *
# from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.live import CryptoDataStream

# TODO 
    # we some how have to get a list of cyptos that we can even play with


wss_client  = CryptoDataStream(ALPACA_KEY, ALPACA_SECRET_KEY)

# async handler
async def quote_data_handler(data):
    # quote data will arrive here
    print(data)

wss_client.subscribe_quotes(quote_data_handler, "BTC/USD")


wss_client.run()