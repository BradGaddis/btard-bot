import csv
import json
import numpy as np
import os
import pandas as pd
import requests 
import time
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoSnapshotRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest
from config import *
from datetime import datetime
from datetime import timedelta
from sklearn.compose import ColumnTransformer,make_column_transformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler


crypto_hist_client = CryptoHistoricalDataClient(api_key=ALPACA_LIVE_KEY, secret_key=ALPACA_LIVE_SECRET_KEY)

crypto_asset = LIVE_END_POINT + '/v2/assets?asset_class=crypto'

def get_cryptos_tradable():
    r = requests.get(crypto_asset, headers={'Apca-Api-Key-Id': ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':ALPACA_LIVE_SECRET_KEY})
    obj = r.content
    output = []
    new_json = obj.decode('utf8').replace("'", '"')
    data = json.loads(new_json)
    for crypto in data:
        if crypto["tradable"]:
            output.append(crypto["symbol"])
    def write_tradeable_crypto():
        file_path = os.path.join(DATA_PATH,"tradable_crypto.csv")
        with open (file_path, "w") as f:
            write = csv.writer(f).writerow(output)
    write_tradeable_crypto()
    return output

def get_live_info():
    pass

def get_snapshot_info_all():
    crypto_list = get_cryptos_tradable()
    output = {}
    request_params = CryptoSnapshotRequest(
        symbol_or_symbols=[crypto for crypto in crypto_list]
    )
    output= crypto_hist_client.get_crypto_snapshot(request_params)
    print(output)
    return output

def historical_data_df(start = None, end = None, minutes_N = 0 , cryptos = ["BTC/USD"], limit = 0):
        # # no keys required for crypto data
        client = CryptoHistoricalDataClient()
        # start = datetime.now() - timedelta(minutes_N)
        
        request_params = CryptoBarsRequest(
                                symbol_or_symbols=cryptos,
                                timeframe=TimeFrame.Minute,
                                start=start,
                                end=end
                        )

        bars = client.get_crypto_bars(request_params)
        cryptos = cryptos
        return get_df(cryptos, bars, limit)

def get_df(cryptos = None, bars = None, limit = 0):
    if not cryptos:
        cryptos = cryptos
    if not bars:
        bars = bars
    output = [bars[crypto] for crypto in cryptos]
    individual = [crypto_bar[:] for crypto_bar in output] # this is a 2d array
    all_dicts = []

    for item in individual:
        for crypto_bar in item:
            all_dicts.append(dict(crypto_bar))

    keys = list(all_dicts[0].keys())
    values = []
    
    for i , item in enumerate(all_dicts):
        values.append([])
        for key in keys:
            values[i].append(item[key])

    df = pd.DataFrame(values,columns=keys)

    columns = ["open", "high","low","close","trade_count","volume","vwap"]
    encode = ["symbol"]
    df_revised = column_scaler(df, columns)
    df_revised = column_encoder(df, encode)
    df_revised.drop(["timestamp"], inplace=True, axis=1)
    
    df_out = df_revised.iloc[-limit:]
    if limit > 0:
        df_out.join(df_revised.iloc[-limit:])
        return df_out
    else:
        return df_revised
    


def column_scaler( df , columns):
    for column in columns:
        arr = np.reshape( np.array(df[column]),(-1,1))
        scaler = MinMaxScaler( )
        df[column] = scaler.fit_transform(arr)
    return df

def column_encoder(df , columns):
    for column in columns:
        # Get one hot encoding of columns B
        one_hot = pd.get_dummies(df[column])
        # Drop column B as it is now encoded
        df = df.drop(column,axis = 1)
        # Join the encoded df
        df = df.join(one_hot)
    return df

# prev_min = 0
# clear = lambda: os.system('cls')
# while True:
#     cur_min = datetime.now().minute
#     if cur_min > prev_min or cur_min == 1:
#         clear()
#         time.sleep(1)
#         get_historical_data_df()
#         prev_min = cur_min
#     # clear()