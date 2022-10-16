from cryptomanager import get_tradable
from config import *
# from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.live import CryptoDataStream
import datetime

# returns all available crypto on Alpaca to trade against
tradable_crypto = get_tradable()


def subscribe_to_quote(symbol = "BTC/USD"):
    wss_client  = CryptoDataStream(ALPACA_PAPER_KEY, ALPACA_PAPER_SECRET_KEY)
    # async handler
    async def quote_data_handler(data):
        # quote data will arrive here
        print(data)
    wss_client.subscribe_quotes(quote_data_handler, symbol)
    wss_client.run()
