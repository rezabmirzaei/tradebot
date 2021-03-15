from typing import List

from stockstats import StockDataFrame

from autotrade.data_fetcher import StockData
from autotrade.indicators import Indicators


class DataEvaluator:

    def __init__(self) -> None:
        self.indicators: Indicators = Indicators()

    def evaluate_stock_list(self, stock_list: List[StockData]) -> List[StockData]:
        evaluated_stock_list: List[StockData] = []
        if not stock_list:
            return evaluated_stock_list
        for stock in stock_list:
            evaluated_stock = self.evaluate_stock(stock)
            evaluated_stock_list.append(evaluated_stock)
        return evaluated_stock_list

    def evaluate_stock(self, stock: StockData) -> StockData:
        # TODO Properly evaluate the stock using necessary indicators and AI
        # TESTING; MACD only atm
        signal = self.indicators.macd(stock.stock_data_frame)
        evaluated_stock = StockData(
            stock.ticker, stock.stock_data_frame, signal)
        return evaluated_stock
