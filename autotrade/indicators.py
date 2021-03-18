from stockstats import StockDataFrame

# Temporary. Necessary indicators will be part of separate project that writes analysed/evaluated data to DB for bot to access.


class Indicators:

    def __init__(self) -> None:
        pass

    def macd(self, stock_data_frame: StockDataFrame) -> str:
        signal = None
        macd = stock_data_frame['macd']
        macd_signal = stock_data_frame['macds']
        # TODO Handle range of data, no need to iterate through it all
        for i in range(1, len(macd_signal)):
            if macd[i] > macd_signal[i] and macd[i - 1] <= macd_signal[i - 1]:
                signal = 'buy'
            elif macd[i] < macd_signal[i] and macd[i - 1] >= macd_signal[i - 1]:
                signal = 'sell'
            else:
                signal = None
        # Return the last calculated signal
        return signal

    def rsi(self, stock_data_frame: StockDataFrame) -> str:
        return None

    def boll(self, stock_data_frame: StockDataFrame) -> str:
        return None
