import datetime
import logging
import os
import time
from configparser import ConfigParser
from os import environ

import alpaca_trade_api as tradeapi

from autotrade.account_manager import AccountManager
from autotrade.data_fetcher import DataFetcher
from autotrade.session_handler import SessionHandler
from autotrade.trade_executor import TradeExecutor

config = ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config', 'prod_config.ini') if environ.get(
    'ENVIRONMENT') == 'PROD' else os.path.join(os.path.dirname(__file__), 'config', 'test_config.ini')
config.read(config_file_path)

logging_filename_master = 'tradebot.log'
logging.basicConfig(filename=logging_filename_master,
                    format='%(asctime)s %(module)s.%(funcName)s %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(logging_filename_master)

# Handle the session and connectivity to Alpaca
sh = SessionHandler(dict(config.items('ALPACA_API')))

# Manage account (money&risk)
am = AccountManager(dict(config.items('MGMT')), sh)

# Retrieve data on stocks to evaluate and potentially trade on
df = DataFetcher(dict(config.items('DATA_API')))

# Execute the actual identified trades
tx = TradeExecutor(sh, am)


# TODO Need better way to schedule this and handle market hours
# TODO Run more often once data is fetched from DB (and updated by external process)

if __name__ == '__main__':
    while True:
        api = sh.api()
        clock = api.get_clock()
        if clock.is_open:
            log.info('Starting a new trading run')
            tx.run(df.stock_data_to_trade_on())
            time_to_wait_seconds = 1200  # 20mins
            log.info(
                'Finished trading run, waiting %s hours for next run', str(
                    datetime.timedelta(seconds=time_to_wait_seconds)))
            time.sleep(time_to_wait_seconds)
        else:
            time_to_open = clock.next_open - clock.timestamp
            time_to_open_seconds = time_to_open.total_seconds()
            log.info('Marked is closed, opens in %s hours', str(
                datetime.timedelta(seconds=time_to_open_seconds)))
            time.sleep(time_to_open_seconds)
