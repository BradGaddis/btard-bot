from curses import keyname
from turtle import end_fill
import requests
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
load_dotenv()

END_POINT = 'https://paper-api.alpaca.markets'

ACCOUNT_URL = END_POINT +  '/v2/account'

key = os.getenv('ALPACA_KEY')
s_key = os.getenv('ALPACA_SECRET_KEY')


# r = requests.get(ACCOUNT_URL, headers={f"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": s_key})

print(r.content)

trading_client = TradingClient(key, s_key)

# filter = ListAccountsRequest(
#                     created_after=datetime.datetime.strptime("2022-01-30", "%Y-%m-%d"),
#                     entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
#                     )

# preparing order data
market_order_data = MarketOrderRequest(
                      symbol="BTC/USD",
                      qty=0.0001,
                      side=OrderSide.BUY,
                      time_in_force=TimeInForce.IOC
                  )

# Market order
market_order = trading_client.submit_order(
                order_data=market_order_data
                )

# def connect(platform = "some platform"):
#     print(f"connecting {platform}")

# def setup():
#     pass