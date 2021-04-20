import alpaca_trade_api as tradeapi


class SessionHandler():

    def __init__(self, config: dict) -> None:
        self.api_key = config['key']
        self.api_secret = config['secret']
        self.base_url = config['base_url']

    def api(self) -> tradeapi.REST:
        return tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
