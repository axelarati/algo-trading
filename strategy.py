import pandas as pd
import numpy as np

import matplotlib.pyplot as plt 

# for computing indicators
from stockstats import StockDataFrame as Sdf # https://pypi.org/project/stockstats/

# backtesting library
# note if you download the anaconda ffn distribution, it will not work correctly
# you need to download the library locally from https://github.com/pmorissette/ffn
import sys
sys.path.insert(0, r'D:\Libraries\ffn-master')
import ffn
import bt

class BacktestUtils:
    @staticmethod
    def plot_backtest(bt_result):
        bt_result.plot()
        plt.title('backtest')
        plt.yscale('log')
        plt.show()

    @staticmethod
    def display_stats(bt_result):
        bt_result.display()

    @staticmethod
    def run_backtest(backtests, prices):
        bts = [bt.Backtest(backtest, prices) for backtest in backtests]
        return bt.run(*bts)

    # test multiple strategies
    # order of bt.algos matters!
    @staticmethod 
    def combine_backtests(backtests):
        return bt.Strategy(
                '{}'.format([b.name for b in backtests]), 
                [bt.algos.RunOnce(),
                 bt.algos.SelectAll(),
                 bt.algos.WeighEqually(),
                 bt.algos.Rebalance()
                 ],
                backtests)

    @staticmethod
    def get_benchmark_bt():
        return bt.Strategy('benchmark', 
                  [bt.algos.RunOnce(),
                   bt.algos.SelectAll(),
                   bt.algos.WeighEqually(),
                   bt.algos.Rebalance()])


class Strategy:

    # each weight is size 1/n 
    @staticmethod
    def _fix_weights(weights):
        return weights/weights.shape[1]

    # portfolio weights always add up to 1 (always fully invested)
    @staticmethod
    def _fully_allocate(weights):
        s = weights.sum(axis=1)
        s = s.where(s!=0,1)
        return weights.div(s,axis=0)

    FIX_WEIGHTS = 'fixed'
    FULLY_ALLOCATE = 'full'

    # historical_data_fetchers is a dict of HistDataFetcher 
    def __init__(self, symbols, historical_data_fetchers, name):
        self.symbols = symbols
        self._historical_data_fetchers = historical_data_fetchers
        self.name = name

        self.close_prices = None
        self.all_prices = None

        self.normalization_func = {
            self.FIX_WEIGHTS: Strategy._fix_weights,
            self.FULLY_ALLOCATE : Strategy._fully_allocate
        }

    # interval is frequency of data, e.g. '3m' = 3 miuntes, '1d' = 1 day
    def get_backtest(self, interval, start, end, weight_normalizer=FIX_WEIGHTS):
        self.gather_prices_and_compute_indicators(interval, start, end)
        weights = self.compute_weights(weight_normalizer)

        # backtests
        return bt.Strategy('{} {} {}'.format(self.name, interval, weight_normalizer), 
                  [bt.algos.WeighTarget(weights),
                   bt.algos.RunEveryNPeriods(1),
                   bt.algos.Rebalance()])

    def gather_prices_and_compute_indicators(self, interval, start, end):
        indicators = self.get_indicators() # implemented in subclasses

        close_prices = []
        all_prices = {}
        symbol_data = { indicator : [] for indicator in indicators }

        for symbol in self.symbols:            
            symbol_prices = self._historical_data_fetchers[symbol].get_historical_prices(interval, start, end)
            close_prices.append(symbol_prices['close'])
            all_prices[symbol] = symbol_prices
            
            symbol_prices = Sdf.retype(symbol_prices)

            for indicator in indicators:
                symbol_data[indicator].append(symbol_prices[indicator])

        # aggregate prices
        close_prices = pd.concat(close_prices,axis=1).fillna(method='ffill') # fill na to catch gaps with missing dates
        close_prices.columns = self.symbols

        self.close_prices = close_prices 
        self.all_prices = all_prices # stored in case more info needs to be computed

        # aggregate indicators
        indicator_vals = {}
        for indicator in indicators:
            df = pd.concat(symbol_data[indicator],axis=1).fillna(method='ffill') 
            df.columns = self.symbols
            indicator_vals[indicator] = df

        self.indicator_vals = indicator_vals

    def compute_weights(self, weight_normalizer):
        weights = self._compute_weights() # implemented in subclasses
        weights = self.normalization_func[weight_normalizer](weights)

        return weights

    def get_indicators(self):
        pass

    def _compute_weights(self):
        pass


class SMACrossover(Strategy):

    def __init__(self,symbols, historical_data_fetchers, params):
        super().__init__(symbols, historical_data_fetchers, 'sma_crossover_{}_{}'.format(params['slow_sma'], params['fast_sma']))

        self.slow_sma = 'close_{}_sma'.format(params['slow_sma'])
        self.fast_sma = 'close_{}_sma'.format(params['fast_sma'])

        self.INDICATORS = [self.slow_sma, self.fast_sma]

    def get_indicators(self):
        return self.INDICATORS

    def _compute_weights(self):
        w = np.where(self.indicator_vals[self.fast_sma] > self.indicator_vals[self.slow_sma], 1, 0)
        w = pd.DataFrame(w,columns=self.symbols).fillna(method='ffill').fillna(0)
        w.index = self.close_prices.index

        return w