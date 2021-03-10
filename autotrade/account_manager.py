import math

from autotrade.session_handler import SessionHandler
from autotrade.data_fetcher import StockData


class AccountManager:

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler: SessionHandler = session_handler

    def account_details(self) -> dict:
        api = self.session_handler.api()
        return api.get_account()

    def order_details(self, stock: StockData) -> dict:
        symbol = str.upper(stock.ticker_symbol())
        signal = stock.signal
        # TODO Current price to bid on. Consider asking price, premarket, volume etc...
        latest_adj_close = stock.stock_data_frame['adj close'][-1]
        buy_price = round(latest_adj_close, 2)
        # TODO Deduce from calculated amount to invest based on RRR
        qty = 2
        # TODO Calculate based on RRR
        take_profit_price = buy_price * 1.1
        # TODO Calculate based on RRR
        stop_loss = buy_price * 0.95
        order_details = {
            'symbol': symbol,
            'signal': signal,
            'qty': qty,
            'bid': buy_price,
            'tfo': take_profit_price,
            'stop_loss': stop_loss
        }
        return order_details

    def kelly_criterion(self, probability: float) -> float:
        edge = 0
        if probability <= 1.5:
            edge = 1
        payout_factor = round(probability - 1, 2)
        percentage_win = math.ceil(1 / probability * 100) + edge
        percentage_loss = 100 - percentage_win
        win_factor = percentage_win / 100
        loss_factor = percentage_loss / 100
        return round((payout_factor * win_factor - loss_factor) / payout_factor, 3)
