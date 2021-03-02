from configparser import ConfigParser

import alpaca_trade_api as tradeapi

# TODO Handle this elsewhere...
config = ConfigParser()
# TODO Configure for different environments (e.g. test/paper vs prod)
config.read('config/paper_account_config.ini')
api_key = config.get('API', 'key')
api_secret = config.get('API', 'secret')
base_url = config.get('API', 'base_url')

api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
account = api.get_account()

print(account)

# Run periodically
# 1. Check existing portfolio and assess positions
#   > 1.a. Sell/close if necessary
# 2. Fetch list of potential buys (algorithmic analysis, select markets/indices)
# 3. Calculate amount to invest based on RRR and general market sentiment (AI)
# 4. Enter positions (buy)
#  > 4.a. Handle stop-loss/TPO etc
# 5 Repeat
