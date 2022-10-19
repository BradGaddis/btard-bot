import requests 
from config import *
import json



def get_cryptos_tradable():
    url = 'https://api.alpaca.markets/v2/assets?asset_class=crypto'
    
    r = requests.get(url, headers={'Apca-Api-Key-Id': ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':ALPACA_LIVE_SECRET_KEY})
    obj = r.content
    output = []
    new_json = obj.decode('utf8').replace("'", '"')
    data = json.loads(new_json)
    for crypto in data:
        if crypto["tradable"]:
            output.append(crypto["symbol"])
    return output
        
print(get_cryptos_tradable())
