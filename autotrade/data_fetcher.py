import json
import logging
from configparser import ConfigParser
from os import environ
from typing import List

import requests

log = logging.getLogger('tradebot.log')


class DataFetcher:

    def __init__(self) -> None:
        config = ConfigParser()
        config_file_path = 'config/prod_config.ini' if environ.get(
            'ENVIRONMENT') == 'PROD' else 'config/test_config.ini'
        config.read(config_file_path)
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
            api_response = requests.get(self.base_url + index)
            data = json.loads(api_response.text)
            api_data.extend(data['stocks'])
        # Remove duplicates
        deduped_stock_list = {each['ticker']: each for each in api_data}.values()
        # The data to trade on, filter only for stocks with buy or sell signal
        stock_data_to_trade_on = [stock for stock in deduped_stock_list if (
            stock['advice'] == 'BUY' or stock['advice'] == 'SELL')]
        return stock_data_to_trade_on
