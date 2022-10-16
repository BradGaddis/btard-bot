import webscraper
from stockinfo import *

class Asset_Picker():
    def get_assets(assets = ["msft"]):
        
        print(f"retreiving assets {assets}")
        
        # TODO
            # detemerine what constitues a stock worth buying
                # the balance sheet must reflect that debt is equal to or less than capital
                # market cap?

        # webscraper.scrape() # somehow save them to a csv or list?
        return assets

    def check_balance_sheet(asset): 
        for i in range(len(asset)):
            check_stock(asset[0])


    # check_balance_sheet("msft")