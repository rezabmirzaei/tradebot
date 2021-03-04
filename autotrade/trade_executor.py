from typing import List

import alpaca_trade_api as tradeapi

from autotrade.data_fetcher import StockData
from autotrade.session_handler import SessionHandler


class TradeExecutor():

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler: SessionHandler = session_handler

    def execute_trades(self, stock_list: List[StockData]) -> None:
        print('Executing trades...')
        # api = self.session_handler.api()
        for stock in stock_list:
            try:
                symbol = stock.ticker_symbol()
                signal = stock.signal
                # TODO Handle all other parameters like limit_price, stop-loss etc

                if signal == 'buy':
                    print("Buying " + symbol)
                    # api.submit_order(symbol=symbol, qty='5', side=signal,
                    #                 type='limit', limit_price='265', time_in_force='day')
                elif signal == 'sell':
                    print("Selling " + symbol)
            except Exception as e:
                # TODO Log failing order and go for the next one
                print('Error (' + symbol + '): ' + str(e))
                continue
