from typing import List

import pandas as pd
import yfinance as yf
from pytickersymbols import PyTickerSymbols
from stockstats import StockDataFrame
from yfinance import Ticker


class StockData:

    def __init__(self, ticker: Ticker, stock_data_frame: StockDataFrame, signal: str) -> None:
        self.ticker: Ticker = ticker
        self.stock_data_frame: StockDataFrame = stock_data_frame
        self.signal: str = signal
        # TODO Add remaining parameters like limit_price, stop-loss etc

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

    def stock_data(self, ticker_symbol: str) -> StockData:
        sdf = StockDataFrame()
        ticker = yf.Ticker(ticker_symbol)
        stock_info = yf.download(ticker_symbol, period='6mo')
        stock_data_frame = sdf.retype(pd.DataFrame(
            stock_info[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]))
        return StockData(ticker, stock_data_frame, None)

    def index_stock_data(self, index_symbol: str) -> List[StockData]:

        index_symbol_lower = str.lower(index_symbol)
        all_ticker_symbols_on_index = []
        try:
            all_ticker_symbols_on_index = list(
                self.tickers_on_index[index_symbol_lower])
        except KeyError:
            print('Can not get tickers for index \'' + index_symbol_lower + '\'')
            return

        print('Getting information for stocks on index ' + index_symbol_lower)

        stock_list: List[StockData] = []
        for ticker in all_ticker_symbols_on_index:
            try:
                stock_list.append(self.stock_data(ticker[1]))
            except Exception as e:
                print(str(e))
                # Nevermind one stock failing, go for the next one
                continue

        return stock_list
