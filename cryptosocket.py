from config import *
# from alpaca.data import CryptoDataStream, StockDataStream
from alpaca.data.live import CryptoDataStream
import datetime

# TODO 
    # we some how have to get a list of cyptos that we can even play with


# wss_client  = CryptoDataStream(ALPACA_KEY, ALPACA_SECRET_KEY)

# # async handler
# async def quote_data_handler(data):
#     # quote data will arrive here
#     print(data)

# wss_client.subscribe_quotes(quote_data_handler, "BTC/USD")


# wss_client.run()

# testing something
from alpaca.broker.client import BrokerClient
from alpaca.broker.requests import ListAccountsRequest
from alpaca.broker.enums import AccountEntities

broker_client = BrokerClient('api-key', 'secret-key')

# search for accounts created after January 30th 2022.
# Response should contain Contact and Identity fields for each account.
filter = ListAccountsRequest(
                    created_after=datetime.datetime.strptime("2022-01-30", "%Y-%m-%d"),
                    entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
                    )

accounts = broker_client.list_accounts(search_parameters=filter)