from price_data import *
from strategy import *

from binance.client import Client

import json
import requests
from datetime import datetime, timedelta, timezone


strategy_type_map = {
    #'rsi' : RSI,
    'sma' : SMACrossover
}

def main(config_file_name, preview, port, strategy_id):
    with open(config_file_name) as config_file:
        config = json.load(config_file)

    print(datetime.utcnow(), 'utc', 'start_time\n')
    
    # create list of all symbols we need data for
    symbols = list(set([symbol for strategy_config in config for symbol in strategy_config['symbols']])) 

    # historical data 
    client = Client()
    #historical_data_fetcher = { symbol : HistDataFetcher(client, symbol) for symbol in symbols }
    historical_data_fetcher = { symbol : RecentDataFetcher(client, symbol) for symbol in symbols }

    # create strategies
    strategies = []
    for strategy_config in config:
        constructor = strategy_type_map[strategy_config['type']]
        strategy = constructor(strategy_config['symbols'], historical_data_fetcher, strategy_config['args'])
        strategies.append((strategy,strategy_config))

    start = datetime(2018,1,1).replace(tzinfo = timezone.utc) # utc time IMPORTANT
    end = datetime.utcnow().replace(tzinfo = timezone.utc)#start_datetime+timedelta(weeks=145)

    # compute and combine weights for all strategies
    tot_weights = pd.DataFrame([np.zeros(len(symbols))],columns=symbols)
    for strategy,strategy_config in strategies:
        strategy.gather_prices_and_compute_indicators(strategy_config['freq'], start, end)
        weights = strategy.compute_weights(Strategy.FIX_WEIGHTS) * strategy_config['weight']
        
        tot_weights[weights.columns] += weights.iloc[-1]

    print('Weights')
    print(tot_weights)

    # if the weights sum up to over 1, we need to normalize them
    w_sum = round(tot_weights.iloc[0].sum(),6)
    if w_sum > 1:
        tot_weights /= w_sum
        print()
        print('Normalizd Weights')
        print(tot_weights)

    # generate signals and send to broker
    print()
    for symbol in symbols:
        weight = round(tot_weights[symbol]*100,2)[0]

        signal = 'LONG {} {} %PORTFOLIO'.format(symbol[:-4], weight)

        print(signal)
        if not preview:
            #print('sending signal')
            r = requests.post('http://localhost:{}/api/strategies/{}?signal={}'.format(port, strategy_id,signal))
            #print(r.text)

    print('-------------------------------------------------')
    print()

# parse arguments
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Choose a strategy')
    parser.add_argument('--config', metavar='str', required=True,
                        help='the strategy type')
    parser.add_argument('--preview', metavar='bool', required=False, default=False,
                        help='preview orders by not sending them to APM')
    parser.add_argument('--port', metavar='int', required=False, default=7430,
                        help='API port for APM')
    parser.add_argument('--strategy_id', metavar='int', required=False, default=1010,
                        help='Strategy ID in APM')

    args = parser.parse_args()
    main(config_file_name=args.config, preview = args.preview, 
         port=args.port, strategy_id = args.strategy_id)
