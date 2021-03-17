import logging
import math
from typing import List

from autotrade.data_fetcher import StockData
from autotrade.session_handler import SessionHandler

log = logging.getLogger('tradebot.log')


class AccountManager:

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler: SessionHandler = session_handler
        self.RRR = 1.8  # Assumes 57% win probability
        self.take_profit_pc = 7
        self.stop_loss_pc = 5

    def account_details(self) -> dict:
        api = self.session_handler.api()
        return api.get_account()

    def open_positions(self) -> List[dict]:
        api = self.session_handler.api()
        return api.list_positions()

    def is_eligible_for_trading(self) -> bool:
        """ Assess wether or not the account is eligable for trading """
        account = self.account_details()
        # TODO NB! Further check on eligibility
        return account.status == 'ACTIVE' and float(account.buying_power) > 1000

    def order_details(self, stock: StockData) -> dict:
        """ Calculate details for an order based on account status and strategy variables """
        symbol = str.upper(stock.ticker_symbol())
        signal = stock.signal
        order_details = {
            'symbol': symbol,
            'signal': signal
        }
        if signal == 'buy':
            latest_adj_close = round(
                stock.stock_data_frame['adj close'][-1], 2)
            buying_power = float(self.account_details().buying_power)
            amount_to_invest = buying_power * self.kelly_criterion(self.RRR)
            qty = math.floor(amount_to_invest / latest_adj_close)
            if qty == 0:
                log.warn(
                    'Cannot create order for %s due to insufficent funds', symbol)
                return None
            take_profit = round(latest_adj_close *
                                (1 + self.take_profit_pc / 100), 2)
            stop_loss = round(latest_adj_close *
                              (1 - self.stop_loss_pc / 100), 2)
            order_details['qty'] = qty
            order_details['limit'] = latest_adj_close
            order_details['take_profit'] = take_profit
            order_details['stop_loss'] = stop_loss

        # TODO Handle sell. Iterate open positions and match with sell signals

        log.info('Order details: %s', order_details)
        return order_details

    def kelly_criterion(self, probability_gain: float) -> float:
        edge = 0
        if probability_gain <= 2:
            edge = 1
        profit_factor = round(probability_gain - 1, 2)
        percentage_gain = math.ceil(1 / probability_gain * 100) + edge
        percentage_loss = 100 - percentage_gain
        win_factor = percentage_gain / 100
        loss_factor = percentage_loss / 100
        return round((profit_factor * win_factor - loss_factor) / profit_factor, 3)
