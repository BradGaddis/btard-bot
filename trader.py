import csv
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from turtle import position
from alpaca.trading.client import TradingClient
from pytz import AmbiguousTimeError
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
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.models import Calendar
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, OrderStatus
from alpaca.trading.requests import ClosePositionRequest
from uuid import UUID
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelEncoder


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
        self.gamblin_monty = self.total_buying_power * .01 if self.total_buying_power > 1 else 1    # the amount of money to just fuck around with
        self.crypto_gamblin_monty = self.total_buying_power * .01 if self.total_buying_power > 1 else 1    
        self.long_term_invest_amount = (self.total_buying_power - self.gamblin_monty - self.crypto_gamblin_monty) * .9

        self.day_trade_allowed = allow_day_trade # false by default

        # if set, will not allow the trader to excede this amount of assets in the portfolio
        self.total_positions_allowed = positions_allowed

        # self.check_set_gambling_params()
        

    ## ---- ##

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
            # self.cur_pos_df.drop("Factor",axis=1,inplace=True) # drop factor from axis 1 and make changes permanent by inplace=True
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

    def cancel_orders(self):
        self.trading_client.cancel_orders()

    # I'm noob and couldn't figure out how to call the damn get_clock() method. Perhaps someone smarter than me can...
    def get_market_time(self):
        r = requests.get(LIVE_END_POINT + "/v2/clock", headers={"APCA-API-KEY-ID": ALPACA_LIVE_KEY, "APCA-API-SECRET-KEY": ALPACA_LIVE_SECRET_KEY})
        obj = r.content
        new_json = obj.decode('utf8').replace("'", '"')
        data = json.loads(new_json)
        print(data)

    def cancel_all_orders(self):
        self.trading_client.cancel_orders()

    def buy_position_at_market(self, ticker, amt = None, notation_or_qty = "qty"):
        
        if not amt:
            amt = self.crypto_gamblin_monty
        trade_result = False

        if self.position_count > self.total_positions_allowed: # TODO add logic to env
            return trade_result
        print("buying ", ticker)
        market_order_data = MarketOrderRequest(
                            symbol=ticker,
                            notional=amt,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.IOC 
                            )

        # Market order
        market_order = self.trading_client.submit_order(
                        order_data=market_order_data
                    )


    def sell_position_market(self, ticker = "ETHUSD", amt = 1, notation_or_qty = "qty"):
        # print(self.positions)
        pos_to_close_id = None
        unrealized_pl = 0
        for position in self.positions:
            position = dict(position)
            print("selling ", ticker)
            if position["symbol"] == ticker:
                pos_to_close_id = position["asset_id"]
                unrealized_pl = float(position["unrealized_pl"])
        close = self.trading_client.close_position(pos_to_close_id)
        return  unrealized_pl


    def get_positions(self):
        # for position in self.positions:
        #     print(position)
        return self.positions
    

    def get_position():
        pass

    def find_potential_new_pos(self):
        pass

    def get_position_tickers(self):
        self.position_count = len(self.positions)
        return [asset.symbol for asset in self.positions]

    def check_set_gambling_params(self):
        #check if params already set
        if os.path.exists(os.path.join(DATA_PATH ,'portfolio_params.csv')):
            with open (os.path.join(DATA_PATH,"portfolio_params.csv"), "r") as params_txt:
                reader = csv.reader(params_txt)
                for row in reader:
                    print(row)

            self.gamblin_monty = self.total_buying_power * .01 if self.total_buying_power > 1 else 1    
            self.crypto_gamblin_monty = 0
            self.long_term_invest_amount = (self.total_buying_power - self.gamblin_monty) * .9
        
        else :
            # set the params if they don't exist
            params = ["gamblin_monty","crypto_gameblin_monty","long_term_invest_amount"]
            with open (os.path.join(DATA_PATH ,"portfolio_params.csv"), "w") as params_txt:
                writer = csv.DictWriter(params_txt, fieldnames=params)
                writer.writeheader()
                writer.writerow(dict({"gamblin_monty": {self.gamblin_monty}}))
                writer.writerow(dict({"crypto_gameblin_monty": {self.crypto_gamblin_monty}}))
                writer.writerow(dict({"long_term_invest_amount": {self.long_term_invest_amount}}))
                


    def get_all_orders_df(self):
        request_params = GetOrdersRequest(
                    status="closed",
                    # side=OrderSide.SELL
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

        # print(keys)

        df = pd.DataFrame(values, columns=keys)
        
        df.filled_at = df.filled_at.apply(lambda x: pd.to_datetime(x))
        df["will_be_day_trade"] = df.filled_at.apply(lambda x: parser.parse(x.strftime('%Y-%m-%d')) +  timedelta(days=1) > datetime.now())
        df.will_be_day_trade = df.will_be_day_trade.apply(lambda x: int(x))

        df = column_onehot_encoder(df, [])
        df = df.iloc[ :,13:]

        df.drop(["time_in_force",],inplace=True, axis=1)


        df.asset_class = df.asset_class.apply(lambda x: str(x).split(".")[1])
        df.order_class = df.order_class.apply(lambda x: str(x).split(".")[1])
        df.status = df.status.apply(lambda x: str(x).split(".")[1])
        df.side = df.side.apply(lambda x: str(x).split(".")[1])
        df.type = df.type.apply(lambda x: str(x).split(".")[1])

        df = column_onehot_encoder(df, ["asset_class","order_class","order_type","status","side","type"])
        df = df.fillna(value=0)
        # df = column_scaler(df, ["filled_qty", "filled_avg_price"])

        df.extended_hours = df.extended_hours.apply(lambda x: int(x))

        def return_dict_by_symbol(df):
            assets = df.symbol.unique()
            df_dict = {}
            for asset in assets:
                df_dict[asset] = df[df.symbol == asset].to_dict()
                # print(df_dict[asset], "\n" )
            return df_dict

        
        return df, return_dict_by_symbol(df)

    def run(self):
        # self.buy_position_at_market("BTC")
        # print(self.get_all_orders_df()[0])
        # test_stuff = self.get_cur_pos_df()[1]

        # for key in test_stuff.keys():
        #     print(test_stuff[key], "\n")

        dict_in = self.get_cur_pos_df()[1]
        for key in dict_in.keys():
            print(key)
            for item in dict_in[key]:
                print(list(item.keys()))
                for item_key in item.keys():
                    print(item[item_key])

        # self.sell_position_market()
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
