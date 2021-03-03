import pandas as pd
import yfinance as yf
from pytickersymbols import PyTickerSymbols
from stockstats import StockDataFrame

pts = PyTickerSymbols()
tickers_on_index = {
    'dow': pts.get_yahoo_ticker_symbols_by_index('DOW JONES'),
    'sp500': pts.get_yahoo_ticker_symbols_by_index('S&P 100'),
    'nasdaq100': pts.get_yahoo_ticker_symbols_by_index('NASDAQ 100'),
    'dax': pts.get_yahoo_ticker_symbols_by_index('DAX'),
    'ftse100': pts.get_yahoo_ticker_symbols_by_index('FTSE 100'),
    'cac40': pts.get_yahoo_ticker_symbols_by_index('CAC 40')
}


def stock_data(ticker_symbol: str) -> StockDataFrame:
    sdf = StockDataFrame()
    stock = yf.download(ticker_symbol, period='6mo')
    stock = sdf.retype(pd.DataFrame(
        stock[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]))
    return stock


def index_stock_data(index: str) -> list:

    index_lower = str.lower(index)
    try:
        tickers_on_index[index_lower]
    except KeyError:
        print('Can not get tickers for index \'' + index_lower + '\'')
        return

    print('Getting information for stocks on index ' + index_lower)

    all_ticker_symbols_on_index = tickers_on_index[index_lower]

    stocks = []
    sdf = StockDataFrame()
    for ticker in list(all_ticker_symbols_on_index):
        try:
            stocks.append(stock_data(ticker[1]))
        except Exception as e:
            print(str(e))
            # Nevermind one stock failing, go for the next one
            continue

    return stocks
