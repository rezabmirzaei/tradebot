import alpaca_trade_api as tradeapi


class SessionHandler():

    def __init__(self, api_key: str, api_secret: str, base_url: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def api(self) -> tradeapi.REST:
        return tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')
