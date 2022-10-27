import csv
import enum
import json
import os
import pandas as pd
import requests 
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoSnapshotRequest
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest
from config import *
from datetime import datetime
from datetime import timedelta


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

def get_historical_data_df(start = None, end = None, minute = None, minutes_N = 0 , cryptos = ["BTC/USD", "ETH/USD"]):
    # # no keys required for crypto data
    client = CryptoHistoricalDataClient()
    start = datetime.now() - timedelta(minutes_N)
    
    request_params = CryptoBarsRequest(
                            symbol_or_symbols=cryptos,
                            timeframe=TimeFrame.Minute,
                            start=None,
                            end=None
                    )

    bars = client.get_crypto_bars(request_params)
    
    output = [bars[crypto] for crypto in cryptos]
    take_last_5 = [crypto_bar[:] for crypto_bar in output] # this is a 2d array
    all_dicts = []

    for item in take_last_5:
        for crypto_bar in item:
            all_dicts.append(dict(crypto_bar))

    keys = list(all_dicts[0].keys())
    values = []
    
    for i , item in enumerate(all_dicts):
        values.append([])
        for key in keys:
            values[i].append(item[key])

    print(pd.DataFrame(values,columns=keys))

    return pd.DataFrame(values,columns=keys)



get_historical_data_df()