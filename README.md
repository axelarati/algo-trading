# algo-trading
This repository provides a generic template for creating your own algo trading system.
It is currently set up to use data from Binance and execute signals using the Alera Portfolio Manager.

## Project Setup
I recommend using Anaconda for the set up. Feel free to set up a separate environment and install the necessary libraries.

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

### Code Structure
There are a few main files in the project. 

#### strategy.py
You can define your strategies here. They should inherit ```Strategy``` and implement ```get_indicators()``` and ```_compute_weights()``` - see the ```SMACrossover``` class for an example implementation. You can also access more data to help compute weights for your strategies using ```self.all_prices```

#### backtesting.ipynb
Notebook for backtesting your strategies. It's set up in a notebook since you will be playing with various different settings. Follow the code in the notebook to get started.

#### price_data.py
This file acts as a utility to retrieve pricing data for both backtesting and strategy execution. 

The class ```HistDataFetcher``` allows for fetching data at given intervals over any period of time. Note that for Binance, only so much data can be retrieved at once. That means if you attempt to get minute data for the last 2 years, it will not work. In order to do something like this, I recommend modifying this class and implementing a way to split and cache data.

The class ```RecentDataFetcher``` quickly fetches the 500 most recent data points for any interval. This class is quick and useful for the actual execution of the strategy (you will notice it is used in ```run_strategy.py```) instead of ```HistDataFetcher```. For backtesting, it is recommended to use ```HistDataFetcher```

#### strategy_config.json

#### run_strategy.py
This file runs the strategies you've defined in ```strategy_config.json```. You will want to edit this file to handle your strategy execution once you compute the weights.
