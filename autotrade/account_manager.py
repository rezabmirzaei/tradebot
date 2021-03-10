import math

from autotrade.session_handler import SessionHandler


class AccountManager:

    def __init__(self, session_handler: SessionHandler) -> None:
        self.session_handler: SessionHandler = session_handler

    def buying_power(self) -> float:
        api = self.session_handler.api()
        account = api.get_account()
        return account.buying_power

    def account_details(self):
        api = self.session_handler.api()
        return api.get_account()

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
