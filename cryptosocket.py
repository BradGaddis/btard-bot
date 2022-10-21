import datetime
from urllib import request
from config import *
# from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.live import CryptoDataStream
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import requests

# returns all available crypto on Alpaca to trade against
# tradable_crypto = get_tradable()

_date = datetime.datetime.strptime("2022-10-01",'%Y-%m-%d')
print(type(_date))


def subscribe_to_quote(symbol = "BTC/USD"):
    wss_client  = CryptoDataStream(ALPACA_PAPER_KEY, ALPACA_PAPER_SECRET_KEY)
    # async handler
    async def quote_data_handler(data):
        # quote data will arrive here
        pass
    wss_client.subscribe_quotes(quote_data_handler, symbol)
    wss_client.run()


# The documention implies that you can simply pass a string. You cannot. It must be in datetime...
def get_historical_data(start = None, end = None, cryptos = ["BTC/USD"]):
    # # no keys required for crypto data
    client = CryptoHistoricalDataClient()

    request_params = CryptoBarsRequest(
                            symbol_or_symbols=cryptos,
                            timeframe=TimeFrame.Day,
                            start=start,
                            end=end
                    )

    bars = client.get_crypto_bars(request_params)

    return bars


r = requests.get("wss://stream.data.alpaca.markets/v1beta2/crypto")
print(r.content)
