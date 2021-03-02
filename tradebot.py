import alpaca_trade_api as tradeapi

from account.session_handler import RestApi

# TODO: Setup proper config handling
# Authentication and connection details
api_key = '...'
api_secret = '...'
base_url = 'https://paper-api.alpaca.markets'

restApi = RestApi(api_key, api_secret, base_url)

print(restApi.trading_api().get_account())
