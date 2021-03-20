# algo-trading
This repository provides a generic template for creating your own algo trading system. It is currently set up to use data from Binance and execute signals using the Alera Portfolio Manager (APM). Of course, you can change the code to trade any assets and use data from any source you like &ndash; this project is designed to help anyone get started.

## Project Setup
I recommend using Anaconda for the set up. Feel free to set up a separate python environment.

This project is designed to help you take historical data use it to create a portfolio. It is essentially providing a templat to create **rotational** strategies, in the sense that, on each execution, the system chooses some number of assets (indicatd by a weight vector) and enters/exits positions for those assets at the market price.

A more complicated system may look to use limit orders to enter positions at a specific price. It is possible to do that using this code template (you would have to create a limit price vector in addition to a weigh vector). However, it is more difficult to backtest such strategies, since you would need to adjust entry prices in the backtester, as well as determine which orders would actually execute. There are backtesting softwares out there that are better suited to this kind of more complex backtesting &ndash; the main caveat being that many of those softwares do not provide proper trade execution.

### Libraries
```
pandas
numpy
bt
ffn -- needs to be manually downloaded and referenced from https://github.com/pmorissette/ffn (see imports in notebooks)
python-binance
stockstats
```
Install/upgrade anything else as necessary.

## Code Structure
There are a few main files in the project. 

#### strategy.py
You can define your strategies here. They should inherit `Strategy` and implement `get_indicators()` and `_compute_weights()` - see the `SMACrossover` class for an example implementation. You can also access more data to help compute weights for your strategies using `self.all_prices`

#### backtesting.ipynb
A notebook for backtesting your strategies &ndash; you will be able to try various different strategy settings. Follow the code in the notebook to get started.

#### price_data.py
This file acts as a utility to retrieve pricing data for both backtesting and strategy execution. 

The class `HistDataFetcher` allows for fetching data at given intervals over any period of time. Note that for Binance, only so much data can be retrieved at once. That means if you attempt to get minute data for the last 2 years, it will not work. In order to do something like this, I recommend modifying this class and implementing a way to split and cache data.

The class `RecentDataFetcher` quickly fetches the 500 most recent data points for any interval. This class is quick and useful for the actual execution of the strategy (you will notice it is used in `run_strategy.py` instead of `HistDataFetcher`). For backtesting, it is recommended to use `HistDataFetcher`

#### strategy_config.json
This file holds the config for the strategies you intend to trade. Please look through the file to see all required parameters.

#### run_strategy.py
This file runs the strategies you've defined in `strategy_config.json`. You will need to add the strategies you create to `strategy_type_map`. Also see the bottom of the file for the arguments needed to run it.

You will want to edit this file to handle your strategy execution in your broker if you don't intend to use APM.

#### strategy_execution_apm_TEMPLATE.bat
This is a sample batch file (that you need to edit) that can be executed by APM in order to run your strategies.
