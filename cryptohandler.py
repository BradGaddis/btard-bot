from config import *
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

# no keys required
client = CryptoHistoricalDataClient()

# single symbol request
request_params = CryptoLatestQuoteRequest(symbol_or_symbols="ETH/USD")

latest_quote = client.get_crypto_latest_quote(request_params)

# must use symbol to access even though it is single symbol
latest_quote["ETH/USD"].ask_price

# print(latest_quote)


##### 

# I could loop through every couple of seconds, but I think I should use a websocket
from alpaca.data import CryptoDataStream, StockDataStream

# keys are required for live data
crypto_stream = CryptoDataStream(ALPACA_KEY, ALPACA_SECRET_KEY)

# keys required
stock_stream = StockDataStream("api-key", "secret-key")