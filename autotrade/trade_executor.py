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

    def run(self, stock_list: List[StockData]) -> None:

        # TODO NB! Check account&market conditions before trading
        # E.g. PDT, market open etc. Notify if issues (email/sms)
        if not self.account_manager.is_eligible_for_trading():
            log.warn('Account is not eligable for trading')
            return

        log.info('Running trades')

        # 1 Update current status of portfolio
        self.update_positions()

        # 2 Sell any remaning stocks as signaled (if still on the books)
        sell_list = list(
            filter(lambda stock: stock.signal == 'buy', stock_list))
        self.sell(sell_list)

        # 3 Buy stocks as signaled
        buy_list = list(
            filter(lambda stock: stock.signal == 'buy', stock_list))
        self.buy(buy_list)

    def update_positions(self) -> None:
        open_positions = self.account_manager.open_positions()
        if open_positions:
            log.info('Updating current positions')
            api = self.session_handler.api()
            for position in open_positions:
                symbol = position.symbol
                qty = int(position.qty)
                unrealized_plpc = float(position.unrealized_plpc)
                # TODO Properly consider this condition
                if unrealized_plpc > (self.account_manager.take_profit_pc / 100):
                    log.info('Selling %s shares of %s', qty, symbol)
                    api.submit_order(
                        symbol=symbol,
                        side='sell',
                        qty=qty,
                        type='market',
                        time_in_force='day'
                    )
        else:
            log.info('No open positions to update')

    def sell(self, sell_list: List[StockData]) -> None:
        log.info('Selling stocks as signaled')
        # TODO sell_list must be filtered to match whatever remains in open positions
        pass

    def buy(self, buy_list: List[StockData]) -> None:
        if buy_list:
            log.info('Buying stocks as signaled')
            api = self.session_handler.api()
            for stock in buy_list:
                signal = stock.signal
                # Safeguard agains wrongful data
                if signal != 'buy':
                    log.warn('Signal was %s, not as expected (buy)', signal)
                    continue
                # Check eligibility before each attempted trade
                # Conditions may have changed since last order was put
                if not self.account_manager.is_eligible_for_trading():
                    log.warn('Account is not eligable for further trading')
                    break
                try:
                    symbol = str.upper(stock.ticker_symbol())
                    order_details = self.account_manager.order_details(stock)
                    if order_details:
                        log.info('Buying %s. Order details: %s',
                                 symbol, order_details)
                        api.submit_order(
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
                        )
                except Exception as e:
                    log.error('Error placing buy order: %s', str(e))
                    continue
        else:
            log.info('Nothing to buy...')
