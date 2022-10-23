import requests 
from config import *
import json
import os
import csv
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoSnapshotRequest

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
    return output
        

def write_tradeable_crypto():
    file_path = os.path.join(DATA_PATH,"tradable_crypto.csv")
    with open (file_path, "w") as f:
        write = csv.writer(f).writerow(get_cryptos_tradable())


def get_live_info():
    pass

def get_historical_info_all():
    crypto_list = get_cryptos_tradable()
    output = {}
    request_params = CryptoSnapshotRequest(
        symbol_or_symbols=[crypto for crypto in crypto_list]
    )
    output= crypto_hist_client.get_crypto_snapshot(request_params)
    print(output)
    return output
    # print(output)
get_historical_info_all()