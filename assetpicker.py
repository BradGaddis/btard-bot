import webscraper

def get_assets(assets = []):
    print(f"retreiving assets {assets}")
    webscraper.scrape()
    # somehow save them to a csv or list?
    return assets


def check_balance_sheet(asset = [ass for ass in range(10)]): # yes, I thought this was funny. I'm childish
    for i in range(len(asset)):
        print(f"checking some value at {i}")
    print("checking balance sheet of some asset...")