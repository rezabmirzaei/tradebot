from configparser import ConfigParser
from os import environ

import alpaca_trade_api as tradeapi


class SessionHandler():

    def __init__(self) -> None:
        config = ConfigParser()
        config_file_path = 'config/live_account_config.ini' if environ.get(
            'ENVIRONMENT') == 'PROD' else 'config/paper_account_config.ini'
        config.read(config_file_path)
        self.api_key = config.get('API', 'key')
        self.api_secret = config.get('API', 'secret')
        self.base_url = config.get('API', 'base_url')

    def api(self) -> tradeapi.REST:
        return tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
