import logging
import math
from typing import List

import alpaca_trade_api as tradeapi

from autotrade.account_manager import AccountManager
from autotrade.data_fetcher import StockData
from autotrade.session_handler import SessionHandler

log = logging.getLogger('tradebot.log')


# TODO Handle market close/open (or near close) for all moves
class TradeExecutor():

    def __init__(self, session_handler: SessionHandler, account_manager: AccountManager) -> None:
        self.session_handler: SessionHandler = session_handler
        self.account_manager: AccountManager = account_manager

    def run(self, stock_list: List[StockData]) -> None:

        # TODO Notify if issues (email/sms)
        # Check more conditions, e.g. PDT, market open etc.
        if not self.account_manager.is_eligible_for_trading():
            log.warn('Account is not eligable for trading')
            return

        log.info('Running trades')

        # 1 Update current status of portfolio
        self.update_positions()

        # 2 Sell any remaning stocks as signaled (if still on the books)
        sell_list = list(
            filter(lambda stock: stock.signal == 'sell', stock_list))
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
                # TODO Consider this condition
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
        if sell_list:
            open_positions = self.account_manager.open_positions()
            if open_positions:
                api = self.session_handler.api()
                for stock_to_sell in sell_list:
                    signal = stock_to_sell.signal
                    symbol = str.upper(stock_to_sell.ticker_symbol())
                    # Safeguard agains wrongful data
                    if signal != 'sell':
                        log.warn('Signal was %s for %s, expected sell',
                                 signal, symbol)
                        continue
                    for position in open_positions:
                        if position.symbol == symbol:
                            log.info(
                                'Closing (selling) open position on %s (qty:%s)', symbol, qty)
                            qty = int(position.qty)
                            api.submit_order(
                                symbol=symbol,
                                side='sell',
                                qty=qty,
                                type='market',
                                time_in_force='day'
                            )
            else:
                log.info('No open positions to close (sell)')
        else:
            log.info('Nothing to sell')

    def buy(self, buy_list: List[StockData]) -> None:
        if buy_list:
            log.info('Buying stocks as signaled')
            open_positions = self.account_manager.open_positions()
            api = self.session_handler.api()
            for stock in buy_list:
                signal = stock.signal
                symbol = str.upper(stock.ticker_symbol())
                # Safeguard agains wrongful data
                if signal != 'buy':
                    log.warn('Signal was %s for %s, expected buy',
                             signal, symbol)
                    continue
                # Check eligibility before each attempted trade
                # Conditions may have changed since last order was put
                # TODO Make sure market isn't near close
                if not self.account_manager.is_eligible_for_trading():
                    log.warn('Account is not eligable for further trading')
                    break
                try:
                    for position in open_positions:
                        # TODO Consider this condition
                        # Don't buy any more if already holding position
                        if not position.symbol == symbol:
                            order_details = self.__buy_order_details(stock)
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
                        else:
                            log.warn(
                                'Already holding position on %s, will not buy more', symbol)
                except Exception as e:
                    log.error('Error placing buy order: %s', str(e))
                    continue
        else:
            log.info('Nothing to buy')

    def __buy_order_details(self, stock: StockData) -> dict:
        symbol = str.upper(stock.ticker_symbol())
        latest_adj_close = round(stock.stock_data_frame['adj close'][-1], 2)
        investment_pc = self.account_manager.investment_pc
        take_profit_pc = self.account_manager.take_profit_pc
        stop_loss_pc = self.account_manager.stop_loss_pc
        account_details = self.account_manager.account_details()
        buying_power = float(account_details.buying_power)
        amount_to_invest = buying_power * (investment_pc / 100)
        qty = math.floor(amount_to_invest / latest_adj_close)
        if qty == 0:
            log.warn(
                'Cannot create order for %s due to insufficent funds', symbol)
            return None
        take_profit = round(latest_adj_close *
                            (1 + take_profit_pc / 100), 2)
        stop_loss = round(latest_adj_close *
                          (1 - stop_loss_pc / 100), 2)
        order_details = {
            'symbol': stock.ticker_symbol(),
            'qty': qty,
            'limit': latest_adj_close,
            'take_profit': take_profit,
            'stop_loss': stop_loss
        }
        return order_details
