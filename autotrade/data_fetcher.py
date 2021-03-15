import logging
from typing import List

import pandas as pd
import yfinance as yf
from pytickersymbols import PyTickerSymbols
from stockstats import StockDataFrame
from yfinance import Ticker

log = logging.getLogger('tradebot.log')


class StockData:

    def __init__(self, ticker: Ticker, stock_data_frame: StockDataFrame, signal: str) -> None:
        self.ticker: Ticker = ticker
        self.stock_data_frame: StockDataFrame = stock_data_frame
        self.signal: str = signal

    def ticker_symbol(self) -> str:
        return self.ticker.info['symbol']


class DataFetcher:

    def __init__(self) -> None:
        pts = PyTickerSymbols()
        self.tickers_on_index = {
            'dow': pts.get_yahoo_ticker_symbols_by_index('DOW JONES'),
            'sp500': pts.get_yahoo_ticker_symbols_by_index('S&P 100'),
            'nasdaq100': pts.get_yahoo_ticker_symbols_by_index('NASDAQ 100'),
            'dax': pts.get_yahoo_ticker_symbols_by_index('DAX'),
            'ftse100': pts.get_yahoo_ticker_symbols_by_index('FTSE 100'),
            'cac40': pts.get_yahoo_ticker_symbols_by_index('CAC 40')
        }

    # TODO Use Alpaca.REST.get_bars
    def stock_data(self, ticker_symbol: str) -> StockData:
        sdf = StockDataFrame()
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf.download(ticker_symbol, period='3mo')
        stock_data_frame = sdf.retype(pd.DataFrame(
            stock_info[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]))
        return StockData(ticker, stock_data_frame, None)

    def index_stock_data(self, index_symbol: str) -> List[StockData]:

        index_symbol_lower = str.lower(index_symbol)
        all_ticker_symbols_on_index = []
        try:
            all_ticker_symbols_on_index = list(
                self.tickers_on_index[index_symbol_lower])
        except KeyError as e:
            log.error('Could not get tickers for index %s\r%s',
                      index_symbol_lower, str(e))
            return

        log.info('Getting information for stocks on index %s',
                 index_symbol_lower)

        stock_list: List[StockData] = []
        for ticker in all_ticker_symbols_on_index:
            try:
                stock_list.append(self.stock_data(ticker[1]))
            except Exception as e:
                log.error('Could not get info for stock %s\r%s',
                          ticker[1], str(e))
                # Nevermind one stock failing, go for the next one
                continue

        return stock_list
