from ast import literal_eval
import requests 
from config import *
import json



def get_tradable():
    url = 'https://api.alpaca.markets/v2/assets?asset_class=crypto'
    r = requests.get(url, headers={'Apca-Api-Key-Id': ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':ALPACA_LIVE_SECRET_KEY})
    obj = r.content
    output = []
    new_json = obj.decode('utf8').replace("'", '"')
    data = json.loads(new_json)
    # s = json.dumps(data, indent=4, sort_keys=False)
    # print(data)
    # print(type(data))
    # print(type(my_json))
    for crypto in data:
        # print(crypto["symbol"])
        output.append(crypto["symbol"])
    return output
        
print(get_tradable())