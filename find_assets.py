import yfinance as yf
import csv
import json
import config
import requests
import os
import pandas as pd
from typing import Tuple

def get_tradable_stocks(output_path: str = config.DATA_PATH, output_format: str = 'csv') -> list[str]:
    """Fetches a list of tradable stocks from the Alpaca API and writes the list to a file.

    Args:
        output_path: The file path to write the list of tradable stocks to.
        output_format: The format of the output file (defaults to 'csv').

    Returns:
        A list of the symbols of tradable stocks.
    """
    # Set the URL of the Alpaca API endpoint
    url = config.LIVE_END_POINT +'assets'

    # Fetch the list of all stocks from the Alpaca API
    response = requests.get(url, headers={'Apca-Api-Key-Id': config.ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':config.ALPACA_LIVE_SECRET_KEY})
    stocks = json.loads(response.content)

    # Filter the list of stocks by the 'class' and 'fractionable' properties
    tradable_stocks = [stock['symbol'] for stock in stocks if stock['class'] == 'us_equity' and stock['fractionable'] and stock['tradable']]

    # Write the list of tradable stocks to a file
    if output_format == 'csv':
        with open(os.path.join(output_path,"tradable_stocks." + output_format), 'w', encoding='utf-8') as f:
            csv.writer(f).writerow(tradable_stocks)
    else:
        raise ValueError(f'Unsupported output format: {output_format}')

    return tradable_stocks

def get_tradable_cryptos(output_path: str = config.DATA_PATH, output_format: str = 'csv') -> list[str]:
    """Fetches a list of tradable crypto assets from the Alpaca API and writes the list to a file.
    Args:
    output_path: The file path to write the list of tradable crypto assets to.
    output_format: The format of the output file (defaults to 'csv').

    Returns:
        A list of the symbols of tradable crypto assets.
    """
    # Set the URL of the Alpaca API endpoint
    url = config.LIVE_END_POINT +'assets'

    # Fetch the list of all assets from the Alpaca API
    response = requests.get(url, headers={'Apca-Api-Key-Id': config.ALPACA_LIVE_KEY, 'Apca-Api-Secret-Key':config.ALPACA_LIVE_SECRET_KEY})
    assets = json.loads(response.content)

    # Filter the list of assets by the 'class' and 'fractionable' properties
    tradable_cryptos = [asset['symbol'] for asset in assets if asset['class'] == 'crypto' and asset['fractionable'] and asset['tradable']]

    # Write the list of tradable crypto assets to a file
    if output_format == 'csv':
        with open(os.path.join(output_path,"tradable_cryptos." + output_format), 'w', encoding='utf-8') as f:
            csv.writer(f).writerow(tradable_cryptos)
    else:
        raise ValueError(f'Unsupported output format: {output_format}')

    return tradable_cryptos

def get_stocks_with_low_market_cap_and_high_cash_debt_ratio():
    # create an empty list to store the stock tickers
    tickers = []

    # loop through all available stock tickers
    for ticker in yf.Tickers('NASDAQ', 'NYSE', 'AMEX'):
        # get the stock info for the current ticker
        stock_info = ticker.info

        # check if the market cap is less than or equal to 3 million and the cash debt ratio is higher than 1
        if stock_info['marketCap'] <= 3000000 and stock_info['cashDebtRatio'] > 1:
            # add the ticker to the list
            tickers.append(ticker)

    # return the list of stock tickers
    return tickers


def check_all_assets(csv_file_path: str = config.DATA_PATH, output_format: str = 'csv') -> tuple[list[dict], pd.DataFrame]:
    """Reads a CSV file containing a list of assets (if it exists), and then loops over the assets
    to get their information from the Yahoo Finance API.
    
    Args:
        csv_file_path: The file path to the CSV file containing the list of assets.
        output_format: The format of the output file (defaults to 'csv').

    Returns:
        A list of dictionaries containing the information for each asset. As well as a DataFrame
    """
    # Create an empty list to store the assets
    assets = []
    
    # Check if the CSV file exists
    if os.path.exists(os.path.join(csv_file_path, "tradable_stocks.csv")):
        # If the CSV file exists, read the list of assets from the file
        with open(os.path.join(csv_file_path, "tradable_stocks.csv"), 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                for subrow in row:
                    assets.append(subrow)
    else:
        # If the CSV file does not exist, get the list of tradable stocks from the Alpaca API
        assets = [asset for asset in get_tradable_stocks()]
    # Create an empty list to store the asset information
    output = []
    # Loop over the assets
    for asset in assets:
        # Create a new list for the asset
        asset_list = []
        
        while True:
            try:
                # Get the asset information
                asset_info = yf.Ticker(asset).info
                
                # Get the asset symbol
                symbol = asset_info["symbol"]
                
                # Append the symbol to the asset list
                asset_list.append(["symbol",symbol])
                
                # Iterate over the key-value pairs in the asset info dictionary
                for key, value in asset_info.items():
                    # Try to convert the value to a float
                    try:
                        value = float(value)
                        # If the conversion is successful, append the key-value pair to the asset list
                        asset_list.append([key, value])
                    except:
                        # If the conversion fails, do nothing
                        pass
                
                # Create a dictionary from the asset list
                asset_dict = dict(asset_list)
                
                # Append the dictionary to the output list
                output.append(asset_dict)

                print(f"Successfully retrieved information for {symbol}.")
                break
            except Exception as e:
                print(e)
                continue
    
    # Create a Pandas DataFrame from the output list
    output_df = pd.DataFrame(output)
    # Save DF to file
    output_df.to_csv(os.path.join(csv_file_path, "asset_info." + output_format), index=False)
    return output, output_df

