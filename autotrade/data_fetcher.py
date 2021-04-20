import json
import logging
from configparser import ConfigParser
from typing import List

import requests

log = logging.getLogger('tradebot.log')


class DataFetcher:

    def __init__(self, config: ConfigParser) -> None:
        self.base_url = config.get('DATA_API', 'base_url')
        # List of indexes to get stock data from for trading
        self.index_list = ['dow', 'nasdaq100', 'sp500']

    def stock_data_to_trade_on(self) -> List[dict]:
        """
        API return list of stock in JSON-format, where each element in list is structured as:
            {
                "ticker":"...",
                "advice":"...",
                "valuation":"..."
            }
        """
        api_data = []
        for index in self.index_list:
            log.info('Getting stock information for index %s', index)
            api_response = requests.get(self.base_url + index)
            data = json.loads(api_response.text)
            api_data.extend(data['stocks'])
        # Remove duplicates (a company may be listen on multiple indexes)
        deduped_stock_list = {each['ticker']: each for each in api_data}.values()
        # The data to trade on, filter only for stocks with buy or sell signal
        stock_data_to_trade_on = [stock for stock in deduped_stock_list if (
            stock['advice'] == 'BUY' or stock['advice'] == 'SELL')]
        return stock_data_to_trade_on
