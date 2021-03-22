import logging
import time

import alpaca_trade_api as tradeapi
import schedule

from autotrade.account_manager import AccountManager
from autotrade.data_evaluator import DataEvaluator
from autotrade.data_fetcher import DataFetcher
from autotrade.session_handler import SessionHandler
from autotrade.trade_executor import TradeExecutor


logging_filename_master = 'tradebot.log'
logging.basicConfig(filename=logging_filename_master,
                    format='%(asctime)s %(module)s.%(funcName)s %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(logging_filename_master)

# Handle the session and connectivity to Alpaca
sh = SessionHandler()

# Manage account (money&risk)
am = AccountManager(sh)

# Retrieve data on stocks to evaluate and potentially trade on
df = DataFetcher()

# Evaluate retrieved data on stocks and assess wether or not to buy/sell
da = DataEvaluator()

# Execute the actual identified trades
tx = TradeExecutor(sh, am)


def run():
    api = sh.api()
    clock = api.get_clock()
    if clock.is_open:
        log.info('Starting a new run')
        stock_list = df.index_stock_data('nasdaq100')
        evaluated_stock_list = da.evaluate_stock_list(stock_list)
        tx.run(evaluated_stock_list)
    else:
        log.info('Marked is closed, waiting')


# TODO Need better way to schedule this and handle market hours
# Run every hour
# TODO Run more often once data is fetched from DB (and updated by external process)
schedule.every(1).hours.do(run)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
