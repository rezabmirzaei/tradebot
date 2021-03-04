import logging
import time

import alpaca_trade_api as tradeapi
import schedule

from autotrade.data_evaluator import DataEvaluator
from autotrade.data_fetcher import DataFetcher
from autotrade.session_handler import SessionHandler
from autotrade.trade_executor import TradeExecutor

log = logging.getLogger(__name__)

# Handle the session and connectivity to Alpaca
sh = SessionHandler()

# Retrieve data on stocks to evaluate and potentially trade on
df = DataFetcher()

# Evaluate retrieved data on stocks and assess wether or not to buy/sell
da = DataEvaluator()

# Execute the actual identified trades
tx = TradeExecutor(sh)


# TESTING

stock_list = df.index_stock_data('dow')
evaluated_stock_list = da.evaluate_stock_list(stock_list)
tx.execute_trades(evaluated_stock_list)

# END TESTING


def run():
    print(time.strftime('%a %d. %Y %H:%M:%S') + ' - Starting a new run...')
    # tx.execute_trades(stock_list)


# Run every 15min
schedule.every(15).minutes.do(run)

# TODO Set up properly once all basic functionality implemented
# while True:
# schedule.run_pending()

# Run periodically
# 1. Check existing portfolio and assess positions
#   > 1.a. Sell/close if necessary
# 2. Fetch list of potential buys (algorithmic analysis, select markets/indices)
# 3. Calculate amount to invest based on RRR and general market sentiment (AI)
# 4. Enter positions (buy)
#  > 4.a. Handle stop-loss/TPO etc
# 5 Repeat
