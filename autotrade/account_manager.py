import logging
from typing import List

from autotrade.session_handler import SessionHandler

log = logging.getLogger('tradebot.log')


class AccountManager:

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler: SessionHandler = session_handler
        # Invest a maximum of 2% of current holding
        self.investment_pc = 2
        # Take profit at 4% gain
        self.take_profit_pc = 4
        # Cover losses at 2% drop
        self.stop_loss_pc = 2

    def account_details(self) -> dict:
        api = self.session_handler.api()
        return api.get_account()

    def open_positions(self) -> List[dict]:
        api = self.session_handler.api()
        return api.list_positions()

    def orders(self, status=None) -> List[dict]:
        api = self.session_handler.api()
        return api.list_orders() if not status else api.list_orders(status=status)

    def is_eligible_for_trading(self) -> bool:
        """ Assess wether or not the account is eligable for trading """
        account = self.account_details()
        # TODO NB! Further check on eligibility
        return account.status == 'ACTIVE' and float(account.buying_power) > 1000
