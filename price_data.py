import pandas as pd
import numpy as np

import os.path

from datetime import datetime, timedelta, timezone
#import dateutil.parser

from binance.client import Client

import json


DATA_COLS = ['open','high','low','close','volume']
KLINE_COLS = ['date'] + DATA_COLS

# returns df of most recent prices with timestamp integers (ms)
def get_prices(client, ticker, interval):
    ohlcv = client.get_klines(symbol=ticker, interval=interval)
    
    data = pd.DataFrame(ohlcv)
    data = data[data.columns[:len(KLINE_COLS)]]
    data.columns = KLINE_COLS

    #print(datetime.utcfromtimestamp(data['date'].iloc[-1]/1000), 'utc', ticker)
    return data.set_index('date').astype('float')

# for a list of tickers
def get_all_prices(client, tickers, interval, column):
    prices = []
    for ticker in tickers:
        print(ticker)
        prices.append(get_prices(client, ticker, interval)[column])
    prices = pd.concat(prices, axis= 1)
    prices.columns = tickers

    return prices

class HistDataFetcher():

    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    # index is formatted using date (not timestamp)
    def get_historical_prices(self, interval, start, end):        
        ohlcv = self.client.get_historical_klines(self.symbol, 
            interval, 
            str(start), 
            str(end))
        
        data = pd.DataFrame(ohlcv)
        data = data[data.columns[:len(KLINE_COLS)]]
        data.columns = KLINE_COLS
        data['date'] = pd.to_datetime(data['date'],unit='ms')
        return data.set_index('date').astype('float')     

 # replicate get_historical_prices of HistDataFetcher, but get most recent data 
class RecentDataFetcher():
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol
 
    def get_historical_prices(self, interval, start, end):
        prices = get_prices(self.client, self.symbol, interval)
        prices.index = pd.to_datetime(prices.index,unit='ms')

        return prices

