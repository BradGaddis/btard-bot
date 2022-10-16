from turtle import end_fill
import requests
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

END_POINT = 'https://paper-api.alpaca.markets'

ACCOUNTURL = END_POINT +  '/v2/account'

print(ACCOUNTURL)

r = requests.get(ACCOUNTURL, headers={f"APCA-API-KEY-ID: {load_dotenv('ALPACA_KEY')}", f"APCA-API-SECRET-KEY: {load_dotenv('ALPACA_SECRET_KEY')}"})

trading_client = TradingClient(load_dotenv('ALPACA_KEY'), load_dotenv('ALPACA_SECRET_KEY'))

# filter = ListAccountsRequest(
#                     created_after=datetime.datetime.strptime("2022-01-30", "%Y-%m-%d"),
#                     entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
#                     )

# # preparing order data
# market_order_data = MarketOrderRequest(
#                       symbol="BTC/USD",
#                       qty=0.0001,
#                       side=OrderSide.BUY,
#                       time_in_force=TimeInForce.DAY
#                   )

# # Market order
# market_order = trading_client.submit_order(
#                 order_data=market_order_data
#                 )

# def connect(platform = "some platform"):
#     print(f"connecting {platform}")

# def setup():
#     pass