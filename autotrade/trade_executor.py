import logging
from typing import List

import alpaca_trade_api as tradeapi

from autotrade.account_manager import AccountManager
from autotrade.data_fetcher import StockData
from autotrade.session_handler import SessionHandler

log = logging.getLogger('tradebot.log')


class TradeExecutor():

    def __init__(self, session_handler: SessionHandler, account_manager: AccountManager) -> None:
        self.session_handler: SessionHandler = session_handler
        self.account_manager: AccountManager = account_manager

    def execute_trades(self, stock_list: List[StockData]) -> None:

        # TODO NB! Check account&market conditions before trading
        # E.g. PDT, market open etc. Notify if issues (email/sms)
        # If not able to autotrade: notify what should have been traded

        log.info('### EXECUTING TRADES')
        api = self.session_handler.api()
        for stock in stock_list:
            # Check eligibility before each attempted trade
            if not self.account_manager.is_eligible_for_trading():
                log.warn('Account is not eligable for further trading')
                break
            try:
                # TODO NB! JUST TESTING!!!
                signal = 'buy'  # stock.signal
                symbol = str.upper(stock.ticker_symbol())
                if signal:
                    order_details = self.account_manager.order_details(stock)
                    if signal == 'buy' and order_details:
                        log.info('Buying %s', symbol)
                        """ api.submit_order(
                            symbol=symbol,
                            side=signal,
                            qty=order_details['qty'],
                            type='market',
                            time_in_force='gtc',
                            order_class='bracket',
                            take_profit=dict(
                                limit_price=order_details['take_profit']
                            ),
                            stop_loss=dict(
                                stop_price=order_details['stop_loss']
                            )
                        ) """
                    elif signal == 'sell':
                        log.info('Selling %s', symbol)
            except Exception as e:
                # TODO Log failing order and go for the next one
                print('Error (' + symbol + '): ' + str(e))
                continue
