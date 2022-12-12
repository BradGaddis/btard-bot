from alpaca.trading.client import TradingClient
import config
from datetime import datetime, timedelta
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest, LimitOrderRequest, MarketOrderRequest
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient

class Alpaca_Trader():
    """
    A class to handle all the Alpaca API calls
    This class will be a paper account instance by default, unless specified otherwise
    """
    def __init__(self, key = config.ALPACA_PAPER_KEY , secret_key = config.ALPACA_PAPER_SECRET_KEY, is_paper = True) -> None:
        # an instance of the trading client
        self.key = key
        self.secret_key = secret_key
        self.trading_client = TradingClient(key,secret_key)
        self.total_account_balance = self.get_account_balance()
        self.amt_allowed_for_trade_us_equity = self.get_allowable_us_equity()
        self.amt_allowed_for_trade_crypto = self.get_allowable_crypto()
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

    def check_asset_type(self, asset):
        return self.trading_client.get_asset(asset).asset_class

    def prevent_day_trade(self, asset, under_25k=False):
        if not asset:
            raise "Asset parameter cannot be None"
        
        if self.total_account_balance > 25000:
            under_25k = True

        # check if asset is crypto
        if self.check_asset_type(asset) == AssetClass.CRYPTO:
            return False

        # loop through get_closed_orders
        for order in self.get_closed_orders():
            # if we find an order that matches the asset, check if it was closed today
            if order.symbol == asset:
                today = datetime.date.today()
                if order.filled_at.date() == today and under_25k:
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
        if self.prevent_day_trade(asset):
            return

        # check asset type
        asset_type = self.check_asset_type(asset)
        if asset_type == AssetClass.CRYPTO:
            amt = amt if amt else self.amt_allowed_for_trade_crypto
        else:
          amt = amt if amt else self.amt_allowed_for_trade_us_equity
        # preparing orders
        market_order_data = MarketOrderRequest(
                            symbol=asset,
                            qty=amt,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.FOK
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

    def sell(self, asset):
        if self.prevent_day_trade(asset):
            return
        # limit sell for what we bought it at
        position = None
        qty = None
        for p in self.get_positions():
            if p.symbol == asset:
                position = p
                break

        if position:
            # Get the average entry price of the position
            entry_price = position.avg_entry_price
            qty = position.qty

        print(f"Attempting to sell {asset} at {entry_price}")
        # preparing orders
        market_order_data = LimitOrderRequest(
                            symbol=asset,
                            qty=qty,
                            limit_price = entry_price,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.FOK
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

    def get_historical_data_df(self, asset, days_delta = 0, start=None):
        if days_delta > 0:
            start = datetime.strptime( str(datetime.now().date() - timedelta(days=days_delta)),'%Y-%m-%d')
        print("start date:" , "Today" if not start else start)
        bars = None
        asset_type = self.check_asset_type(asset)
        if asset_type == AssetClass.CRYPTO:
            client = CryptoHistoricalDataClient()
            params = CryptoBarsRequest(
                        symbol_or_symbols=asset,
                        timeframe=TimeFrame.Minute,
                        start=start
                        )
            bars = client.get_crypto_bars(params)

            # convert to dataframe
        elif asset_type == AssetClass.US_EQUITY:
            asset = [asset]
            client = StockHistoricalDataClient(config.ALPACA_LIVE_KEY, config.ALPACA_LIVE_SECRET_KEY)
            request_params = StockBarsRequest(
                                    symbol_or_symbols=asset,
                                    timeframe=TimeFrame.Minute,
                                    start=start,
                            )

            bars = client.get_stock_bars(request_params)
            
        df = bars.df
    
        df.reset_index(inplace=True)
        df = df.rename(columns={"timestamp":"Date", "open":"Open", "high":"High","low":"Low","close":"Close","volume":"Volume", "trade_count" : "Trade_Count", "vwap": "VWAP"})
        df = df.drop("symbol", axis=1)
        df.Date = df.Date.apply(lambda x: x.to_pydatetime().strftime("%Y-%m-%d %H:%M"))
        df = df.iloc[:,0:-1]
        
        return df
            

        
alp_trade = Alpaca_Trader()

print(alp_trade.get_historical_data_df("AAPL", 1))