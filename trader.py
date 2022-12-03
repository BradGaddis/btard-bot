import csv
from datetime import datetime
from datetime import timedelta
from turtle import position
from alpaca.trading.client import TradingClient
import assetpicker
from config import *
import pandas as pd
import asyncio as asy
import yfinance as yf
import time
import concurrent.futures
import math
import numpy as np
import os
import requests
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import Calendar
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, OrderStatus
from alpaca.trading.requests import ClosePositionRequest
from uuid import UUID
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelEncoder
import cryptomanager

from dateutil import parser

from cryptomanager import historical_data_df

class trader_agent():
    def __init__(self, key = ALPACA_PAPER_KEY, skey = ALPACA_PAPER_SECRET_KEY, paper = True, positions_allowed = math.inf, allow_day_trade = False) -> None:
        """Trading object: Instanciates to paper account by default, unless specified otherwise."""
        
        self.trading_client = TradingClient(key, skey)
        
        # this sets up an array of positons that are currently in the account
        self.positions = self.trading_client.get_all_positions()

        self.pos_keys = []
        self.pos_values = []    
        self.cur_pos_df = self.get_cur_pos_df()
        self.position_count = len(self.positions)

        # 10% remains in cash for manual buying, should one choose to
        self.total_buying_power = float(self.trading_client.get_account().non_marginable_buying_power)
        self.initial_balance = self.set_total_balance()
        self.gamblin_monty = self.set_gramblin_monty()    # the amount of money to just fuck around with
        self.crypto_gamblin_monty =self.set_crypto_gamblin_monty()   

        self.day_trade_allowed = allow_day_trade # false by default

        # if set, will not allow the trader to excede this amount of assets in the portfolio
        self.total_positions_allowed = positions_allowed

        self.isOpen = self.trading_client.get_clock().is_open

    def set_total_balance(self):
        """Sets the initial balance of the account"""
        self.initial_balance = float(self.trading_client.get_account().non_marginable_buying_power)
        # check if initial_balance.txt exists
        if os.path.exists(os.path.join(DATA_PATH ,"initial_balance.txt")):
            # check if balance is greater than the initial balance in the file
            with open(os.path.join(DATA_PATH ,"initial_balance.txt"), "r") as f:
                if self.initial_balance > float(f.read()):
                    # if so, update the file
                    with open(os.path.join(DATA_PATH ,"initial_balance.txt"), "w") as f:
                        print("Updating total balance")
                        f.write(str(self.initial_balance))
                        return self.initial_balance
                else:
                    # if not, return the initial balance in the file
                    with open(os.path.join(DATA_PATH ,"initial_balance.txt"), "r") as f:
                        self.initial_balance = float(f.read())
                        return self.initial_balance                    
        else:
            # if not, create the file
            with open(os.path.join(DATA_PATH ,"initial_balance.txt"), "w") as f:
                f.write(str(self.initial_balance))
                return self.initial_balance




    def set_gramblin_monty(self, amount = None, rewrite = False):
        # check if gamblin_balance.txt exists
        def write_path():
            with open(os.path.join(DATA_PATH ,"gamblin_balance.txt"), "w") as f:
                self.gamblin_monty = amount if amount else self.initial_balance * .25 if self.initial_balance > 1 else 1
                f.write(str(self.gamblin_monty))
                return self.gamblin_monty

        if os.path.exists(os.path.join(DATA_PATH ,"gamblin_balance.txt")):
            if rewrite:
                return write_path()
            with open(os.path.join(DATA_PATH ,"gamblin_balance.txt"), "r") as f:
                self.gamblin_monty = float(f.read())
                return self.gamblin_monty
        else:
            return write_path()

    def set_crypto_gamblin_monty(self, amount = None, rewrite = False):
        # check if gamblin_balance.txt exists
        def write_path():
            with open(os.path.join(DATA_PATH ,"crypto_gamblin_balance.txt"), "w") as f:
                self.crypto_gamblin_monty = amount if amount else self.initial_balance * .25 if self.initial_balance > 1 else 1
                f.write(str(self.crypto_gamblin_monty))
                return self.crypto_gamblin_monty
        if os.path.exists(os.path.join(DATA_PATH ,"crypto_gamblin_balance.txt")):
            if rewrite:
                return write_path()
            with open(os.path.join(DATA_PATH ,"crypto_gamblin_balance.txt"), "r") as f:
                self.crypto_gamblin_monty = float(f.read())
                return self.crypto_gamblin_monty
        else:
            return write_path()


    def get_cur_pos_df(self):
        """Returns a dataframe of the current positions held in portfolio"""
        self.positions = self.trading_client.get_all_positions()
        if len(self.positions) > 0:
            self.pos_keys = [pos[0] for pos in self.positions[0]] 
            self.pos_values = []

            for i , pos in enumerate(self.positions):
                self.pos_values.append([])
                for tup in pos:
                    self.pos_values[i].append((tup[1]))

            self.cur_pos_df = pd.DataFrame(self.pos_values, columns=self.pos_keys)
            self.cur_pos_df.drop(["asset_id", "exchange"], inplace=True, axis=1)
            self.cur_pos_df.asset_class = self.cur_pos_df.asset_class.apply(lambda x: x.split(".")[0])
            self.cur_pos_df.side = self.cur_pos_df.side.apply(lambda x: x.split(".")[0])
            self.cur_pos_df = column_onehot_encoder(self.cur_pos_df, ["side", "asset_class"])

            self.cur_pos_df = self.cur_pos_df.reset_index()
            self.cur_pos_df.drop("index", inplace=True, axis=1)
            self.cur_pos_df.set_index(self.cur_pos_df.symbol, inplace=True)
            self.cur_pos_df = self.cur_pos_df.iloc[:, 1:]
            self.cur_pos_df["us_equity"] = pd.get_dummies(0)
            self.cur_pos_df.fillna(value=0, inplace=True)


            def return_dict_by_symbol(df):
                df_dict = {}
                for i, ind in enumerate(df.index):
                    df_dict[ind] = []
                    for j, col in enumerate(df.columns):
                        df_dict[ind].append({col : df.iloc[i, j]})
                # print(df_dict, "\n")
                            
                return df_dict

            return self.cur_pos_df, return_dict_by_symbol(self.cur_pos_df)
        else:
            return None

    # I'm noob and couldn't figure out how to call the damn get_clock() method. Perhaps someone smarter than me can...
    def get_market_time(self):
        r = requests.get(LIVE_END_POINT + "/v2/clock", headers={"APCA-API-KEY-ID": ALPACA_LIVE_KEY, "APCA-API-SECRET-KEY": ALPACA_LIVE_SECRET_KEY})
        obj = r.content
        new_json = obj.decode('utf8').replace("'", '"')
        data = json.loads(new_json)
        print(data)
        return data

    def cancel_all_orders(self):
        self.trading_client.cancel_orders()

    def get_get_asset_type(self, symbol):
        """Returns the asset type of the symbol"""
        return self.trading_client.get_asset(symbol).asset_class

    def prevent_trade(self):
        # update total buying power
        self.total_buying_power = float(self.trading_client.get_account().buying_power)
        # check if available cash is less than gamblin_monty or crypto_gamblin_monty
        if self.total_buying_power <= float(self.gamblin_monty) or float(self.total_buying_power) <= float(self.crypto_gamblin_monty):
            return True
        return False

    def prevent_day_trade(self, symbol):
        """Returns True if the market is closed, or if the account is not allowed to day trade under conditions."""
        if self.get_get_asset_type(symbol) == "crypto":
            return False

        if float(self.initial_balance) < 25000:
            self.day_trade_allowed = False
        else:
            self.day_trade_allowed = True
            
        if self.trading_client.get_clock().is_open == False:
            print("Market is closed")
            return True
        elif self.day_trade_allowed == False:
            self.positions = self.trading_client.get_all_positions()
            # check position for symbol
            if symbol in [pos.symbol for pos in self.positions]:
                # check if order filled was today
                # loop through orders to find symbol
                orders = self.get_all_orders()
                for order in orders:
                    if order.symbol == symbol:
                        # check if order was today
                        if order.submitted_at.date() == datetime.datetime.now().date():
                            print("Day trade prevented")
                            return True
            else:
                return False
            return True
        else:
            return False

    def buy_position_at_market(self, ticker="BTC/USD", amt = None, notation_or_qty = "qty"):
        """Buys a position at market price"""
        if self.prevent_trade():
            return

        if self.prevent_day_trade(ticker):
            print(f"{ticker} not bought; could be day trade.")
            return

        self.cancel_all_orders()
        
        self.reset_available_gambling_money(ticker)
        
        # check asset type of ticker
        asset = self.get_get_asset_type(ticker);

        if amt:
            amt = self.crypto_gamblin_monty
        elif asset == "us_equity":
            amt = self.gamblin_monty
        elif asset == "crypto":
            amt = self.crypto_gamblin_monty
        trade_result = False

        timeInFore = TimeInForce.IOC if asset == "crypto" else TimeInForce.DAY

        print("buying ", ticker)
        market_order_data = MarketOrderRequest(
                            symbol=ticker,
                            notional=amt,
                            side=OrderSide.BUY,
                            time_in_force=timeInFore 
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )
        print(market_order)

    def sell_position_limit(self, ticker = "BTCUSD"):
        if self.prevent_day_trade(ticker):
            print(f"{ticker} not sold; could be day trade.")
            return
        # cancel all orders
        self.cancel_all_orders()
        self.reset_available_gambling_money(ticker)
        check = False
        amt = 0
        entry_price = 0

        # check asset type of ticker
        asset = self.get_get_asset_type(ticker);

        timeInFore = TimeInForce.IOC if asset == "crypto" else TimeInForce.DAY

        
        for position in self.positions:
                position = dict(position)

                if position["symbol"] == ticker:

                    check = ticker
                    entry_price = math.trunc(float(position['cost_basis']))
                    amt = round(float(position['market_value']),2)

                    print("selling ", ticker, " at ", entry_price, " for ", amt)

        if not check:
            return
        limit_order_data = LimitOrderRequest(
                    symbol=ticker,
                    limit_price=entry_price,
                    notional=amt,
                    side=OrderSide.SELL,
                    time_in_force=timeInFore
                    )
        # Limit order
        limit_order = self.trading_client.submit_order(
                        order_data=limit_order_data
                    )

    def reset_available_gambling_money(self, ticker):
        self.initial_balance = self.set_total_balance()
        
        if self.get_get_asset_type(ticker) == "crypto":
            self.crypto_gamblin_monty = self.set_crypto_gamblin_monty()
        else:
            self.gamblin_monty = self.set_gramblin_monty()

    def sell_position_market(self, ticker="BTC/USD", amt = 1, ninety_percent = True):
        check = None
        if ninety_percent:
            for position in self.positions:
                position = dict(position)
                if position["symbol"] == ticker:
                    check = ticker
                    amt = round(float(position['qty']) * .9, 9)
        
        if not check:
            return
        market_order_data = MarketOrderRequest(
                            symbol=ticker,
                            qty=amt,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.IOC 
                            )

        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )

        print("selling: ", check, amt)

    def get_positions(self):
        return self.trading_client.get_all_positions()


    def get_position_tickers(self):
        self.position_count = len(self.positions)
        return [asset.symbol for asset in self.positions]


    def get_all_orders(self):
        request_params = GetOrdersRequest(
                    status="closed",
                 )
        return self.trading_client.get_orders(filter=request_params)

    def get_all_orders_df(self):
        request_params = GetOrdersRequest(
                    status="closed",
                 )

        # orders that satisfy params
        orders = self.trading_client.get_orders(filter=request_params)
        # print(orders)
        order_dicts = [dict(order) for order in orders]
        keys = list(order_dicts[0].keys())
        values = []
        print(keys)
        for i,order in enumerate(order_dicts):
            values.append([])
            for key in (keys):
                values[i].append(order[key])


        df = pd.DataFrame(values, columns=keys)
        
        df.filled_at = df.filled_at.apply(lambda x: pd.to_datetime(x))
        df["will_be_day_trade"] = df.filled_at.apply(lambda x: parser.parse(x.strftime('%Y-%m-%d')) +  timedelta(days=1) > datetime.now())
        df.will_be_day_trade = df.will_be_day_trade.apply(lambda x: int(x))


        df = df.reset_index(drop=True)
        df.set_index(df.id, inplace=True)



        df = df.iloc[ :,13:]

        df.drop(["time_in_force",],inplace=True, axis=1)


        df.asset_class = df.asset_class.apply(lambda x: str(x).split(".")[1])
        df.order_class = df.order_class.apply(lambda x: str(x).split(".")[1])
        df.status = df.status.apply(lambda x: str(x).split(".")[1])
        df.side = df.side.apply(lambda x: str(x).split(".")[1])
        df.type = df.type.apply(lambda x: str(x).split(".")[1])

        df = column_onehot_encoder(df, ["symbol","asset_class","order_class","order_type","status","side","type"])
        df = df.fillna(value=0)

        df.extended_hours = df.extended_hours.apply(lambda x: int(x))
        print(df)
        
        return df

    def run(self):
        print(self.prevent_trade())
        pass
        

def column_onehot_encoder(df_in , columns):
    for column in columns:
        # Get one hot encoding of columns B
        one_hot = pd.get_dummies(df_in[column])
        # Drop column B as it is now encoded
        df_in = df_in.drop(column,axis = 1)
        # # Join the encoded df
        df_in = df_in.join(one_hot)
    return df_in

def column_scaler( df , columns):
    for column in columns:
        arr = np.reshape( np.array(df[column]),(-1,1))
        scaler = MinMaxScaler( )
        df[column] = scaler.fit_transform(arr)
    return df
