from configparser import ConfigParser

import alpaca_trade_api as tradeapi

from account.session_handler import RestApi

# TODO Handle this elsewhere...
config = ConfigParser()
# TODO Configure for different environments (e.g. test/paper vs prod)
config.read('config/paper_account_config.ini')
api_key = config.get('API', 'key')
api_secret = config.get('API', 'secret')
base_url = config.get('API', 'base_url')

restApi = RestApi(api_key, api_secret, base_url)
print(restApi.trading_api().get_account())

