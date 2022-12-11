from alpaca.trading.client import TradingClient
import config
from datetime import datetime, timedelta
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, OrderStatus

class Alpaca_Trader():
    """
    A class to handle all the Alpaca API calls
    This class will be a paper account instance by default, unless specified otherwise
    """
    def __init__(self, key = config.ALPACA_PAPER_KEY , secret_key = config.ALPACA_PAPER_SECRET_KEY, is_paper = True) -> None:
        # an instance of the trading client
        self.trading_client = TradingClient(key,secret_key)
        self.total_account_balance = self.get_account_balance()
        self.amt_allowed_for_trade_us_equity = self.get_allowable_us_equity()
        self.market_justOpened = True
        self.market_isOpen = self.check_market_isOpen()
        self.get_positions()

    def get_account_balance(self):
        return float(self.trading_client.get_account().non_marginable_buying_power)

    def get_allowable_us_equity(self):
        # amount is, at most, 1% of available balance or $1. Whichever is greater
        percent_of_balance = self.total_account_balance * 0.01
        return max(percent_of_balance, 1)

    def get_allowable_crypto(self):
        # amount is, at most, 1% of available balance or $1. Whichever is greater
        percent_of_balance = self.total_account_balance * 0.01
        return max(percent_of_balance, 1)

    def check_market_isOpen(self):
        return self.trading_client.get_clock().is_open

    def get_positions(self):
        return self.trading_client.get_all_positions()

    def prevent_trade(self, asset):
        if not asset:
            raise "Asset parameter cannot be None"
        
        # if asset is crypto, return False
        for position in self.get_positions():
            # check if is in self.get_positions()
            if position.symbol == asset:
                if position.asset_class == AssetClass.CRYPTO:
                    return False

        # loop through get_closed_orders
        for order in self.get_closed_orders():
            # if we find an order that matches the asset, check if it was closed today
            print(order.symbol)
            if order.symbol == asset:
                today = datetime.date.today()
                if order.filled_at.date() == today:
                    print(f"{asset} will be day traded. Skipping this order")
                    return True

        # otherwise return False
        return False


    def get_closed_orders(self):
        # params to filter orders by
        request_params = GetOrdersRequest(
                            status='closed',
                            # side=OrderSide.SELL
                        )

        # orders that satisfy params
        orders = self.trading_client.get_orders(filter=request_params)
        return orders

    def buy(self, asset, amt):
        if self.prevent_trade(asset):
            return

    def sell(self, asset, amt):
        if self.prevent_trade(asset):
            return

alp_trade = Alpaca_Trader()

print(alp_trade.prevent_trade("SPY"))