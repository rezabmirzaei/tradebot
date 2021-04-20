from configparser import ConfigParser

import alpaca_trade_api as tradeapi


class SessionHandler():

    def __init__(self, config: ConfigParser) -> None:
        self.api_key = config.get('ALPACA_API', 'key')
        self.api_secret = config.get('ALPACA_API', 'secret')
        self.base_url = config.get('ALPACA_API', 'base_url')

    def api(self) -> tradeapi.REST:
        return tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
