from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IntParameter
import numpy as np

class CHOP(IStrategy):
    """
    Example strategy that uses the Choppiness Index approximation for trading signals.
    """
    INTERFACE_VERSION = 3
    
    # Define the Choppiness Index period and the threshold for buying and selling.
    ci_period = 14
    buy_threshold = IntParameter(low=20, high=40, default=30, space='buy')
    sell_threshold = IntParameter(low=60, high=80, default=70, space='sell')

    # Define other strategy parameters (adjust these based on your strategy needs)
    minimal_roi = {"0": 0.01}
    stoploss = -0.1
    timeframe = '5m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # True Range
        dataframe['tr'] = ta.TRANGE(dataframe)

        # Sum of True Range for CI period
        dataframe['tr_sum'] = dataframe['tr'].rolling(window=self.ci_period).sum()

        # Highest high and lowest low for CI period
        dataframe['high_max'] = dataframe['high'].rolling(window=self.ci_period).max()
        dataframe['low_min'] = dataframe['low'].rolling(window=self.ci_period).min()

        # Approximate Choppiness Index calculation
        dataframe['ci'] = 100 * np.log10(dataframe['tr_sum'] / (dataframe['high_max'] - dataframe['low_min'])) / np.log10(self.ci_period)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Buy signal: CI is below the buy threshold, suggesting less choppiness (more trending)
        dataframe.loc[
            (dataframe['ci'] < self.buy_threshold.value),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Sell signal: CI is above the sell threshold, suggesting increased choppiness
        dataframe.loc[
            (dataframe['ci'] > self.sell_threshold.value),
            'sell'] = 1

        return dataframe
