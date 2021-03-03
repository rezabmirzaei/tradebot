import time

import alpaca_trade_api as tradeapi
import schedule

from account.session_handler import SessionHandler
from trade.trade_handler import TradeHandler

session_handler = SessionHandler()
trade_handler = TradeHandler(session_handler)


def run():
    print(time.strftime('%a %d. %Y %H:%M:%S') + ' - Starting a new run...')
    trade_handler.handle_positions()
    trade_handler.execute_trades()


# Run every 15min
schedule.every(15).minutes.do(run)

# TODO Set up properly once all basic functionality implemented
# while True:
#    schedule.run_pending()

# Run periodically
# 1. Check existing portfolio and assess positions
#   > 1.a. Sell/close if necessary
# 2. Fetch list of potential buys (algorithmic analysis, select markets/indices)
# 3. Calculate amount to invest based on RRR and general market sentiment (AI)
# 4. Enter positions (buy)
#  > 4.a. Handle stop-loss/TPO etc
# 5 Repeat
