from configparser import ConfigParser

import alpaca_trade_api as tradeapi


class SessionHandler():

    def __init__(self) -> None:
        config = ConfigParser()
        # TODO Configure for different environments (e.g. test/paper vs prod)
        config.read('config/paper_account_config.ini')
        self.api_key = config.get('API', 'key')
        self.api_secret = config.get('API', 'secret')
        self.base_url = config.get('API', 'base_url')

    def api(self) -> tradeapi.REST:
        return tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
