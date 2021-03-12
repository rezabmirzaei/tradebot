from typing import List

import alpaca_trade_api as tradeapi

from autotrade.data_fetcher import StockData
from autotrade.session_handler import SessionHandler
from autotrade.account_manager import AccountManager


class TradeExecutor():

    def __init__(self, session_handler: SessionHandler, account_manager: AccountManager) -> None:
        self.session_handler: SessionHandler = session_handler
        self.account_manager: AccountManager = account_manager

    def execute_trades(self, stock_list: List[StockData]) -> None:
        print('Executing trades...')
        api = self.session_handler.api()
        for stock in stock_list:
            symbol = str.upper(stock.ticker_symbol())
            try:
                order_details = self.account_manager.order_details(stock)
                print(order_details)

                signal = order_details['signal']
                if signal == 'buy':
                    print('Buying ' + symbol)
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
                elif signal == 'sell':
                    print('Selling ' + symbol)
            except Exception as e:
                # TODO Log failing order and go for the next one
                print('Error (' + symbol + '): ' + str(e))
                continue
