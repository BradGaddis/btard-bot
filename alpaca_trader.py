from alpaca.trading.client import TradingClient
import config
from datetime import datetime, timedelta
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest, LimitOrderRequest, MarketOrderRequest
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from finta import TA
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

    def buy(self, asset, amt = None):
        if self.prevent_day_trade(asset):
            return

        # check asset type
        asset_type = self.check_asset_type(asset)
        print(asset_type)
        print(f"Attempting to buy {asset} at {amt}")
        if asset_type == AssetClass.CRYPTO:
            amt = amt if amt else self.amt_allowed_for_trade_crypto
        else:
          amt = amt if amt else self.amt_allowed_for_trade_us_equity
        # preparing orders
        market_order_data = MarketOrderRequest(
                            symbol=asset,
                            qty=amt,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.IOC
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

    def sell(self, asset):
        if self.prevent_day_trade(asset):
            return
        # limit sell for what we bought it at
        asset_type = self.check_asset_type(asset)
        if asset_type == AssetClass.CRYPTO:
            # remove the / from the asset name
            asset = asset.replace("/", "")
            print(asset)
        position = None
        qty = None
        entry_price = None
        for p in self.get_positions():
            if p.symbol == asset:
                position = p
                break

        if position:
            # Get the average entry price of the position
            entry_price = position.avg_entry_price
            qty = position.qty
            print(f"Position found for {asset}. Qty: {qty} Entry Price: {entry_price}")

        print(f"Attempting to sell {asset} at {entry_price}")
        # preparing orders
        market_order_data = LimitOrderRequest(
                            symbol=asset,
                            qty=qty,
                            limit_price = entry_price,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.IOC
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

    def get_historical_data_df(self, asset = "BTC/USD", days_delta = 0, start=None):
        if days_delta > 0:
            start = datetime.strptime( str(datetime.now().date() - timedelta(days=days_delta)),'%Y-%m-%d')
        print("start: ", start if start else "Today")
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
        df = df.drop("Date", axis=1)
        df = df.iloc[:,0:-1]
        
        return df

    def Historical_Add_Technicals_DF(self, df = None, **kwargs):
        asset = None
        days_delta = 0
    
        if df == None:
            if "asset" in kwargs:
                asset = kwargs["asset"]
                del kwargs["asset"]
            if "days_delta" in kwargs:
                days_delta = kwargs["days_delta"]
                del kwargs["days_delta"]
            if asset or  days_delta:
                df = self.get_historical_data_df(asset=asset, days_delta=days_delta)

        # df['OBV'] = TA.OBV(df)
        df['EMA'] = TA.EMA(df, 200)
        df['RSI'] = TA.RSI(df)
        df  = df.join(TA.PIVOT_FIB(df))
        df = df.join(TA.MACD(df))
        df.fillna(0, inplace=True)
        return df

        
    # def Historical_Add_Technicals_DF(self, df = None, **kwargs):
    #     """
    #     A method that adds technical indicators to a historical data DataFrame.

    #     :param df: (optional) the DataFrame to add the indicators to. If not provided, will use the default historical data DataFrame.
    #     :param kwargs: the technical indicators to add. The keywords should be the names of the indicators (e.g. "EMA", "RSI") and the values should be the parameters to pass to the indicator function (e.g. 200 for the EMA with a window of 200).
    #     :return: the DataFrame with the added technical indicators.
    #     """
    #     # Get asset from kwargs
    #     asset = None
    #     days_delta = 0
    
    #     if df == None:
    #         if "asset" in kwargs:
    #             asset = kwargs["asset"]
    #             del kwargs["asset"]
    #         if "days_delta" in kwargs:
    #             days_delta = kwargs["days_delta"]
    #             del kwargs["days_delta"]
    #         if not asset or not days_delta:
    #             df = self.get_historical_data_df(asset=asset, days_delta=days_delta)

    #         df = self.get_historical_data_df()
            
    #     # Add each of the technical indicators specified in kwargs
    #     for indicator, params in kwargs.items():
    #         df[indicator] = TA.indicator(*params)
            
    #     # Fill any missing values with 0 and return the DataFrame
    #     df.fillna(0, inplace=True)
    #     return df

