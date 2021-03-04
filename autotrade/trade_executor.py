import alpaca_trade_api as tradeapi

from autotrade.session_handler import SessionHandler


class TradeExecutor():

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler = session_handler

    def handle_positions(self) -> None:
        print('Handling positions...')
        pass

    def execute_trades(self) -> None:
        print('Executing trades...')
        # Test
        # self.api.submit_order(symbol='FB', qty='5', side='buy',
        #                      type='limit', limit_price='265', time_in_force='day')
        pass
