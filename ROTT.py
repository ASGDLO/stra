from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import numpy as np
import pandas as pd
import talib.abstract as ta
from freqtrade.strategy import DecimalParameter, IntParameter

class ROTT(IStrategy):
    # Strategy parameters
    timeframe = '1m'
    stoploss = -0.1
    minimal_roi = {
        "60": 0.01
    }

    # Parameters for 'buy' space
    x1 = IntParameter(5, 50, default=30, space='buy')
    x2 = IntParameter(50, 1500, default=1000, space='buy')

    # Parameters for 'sell' space
    sell_x1 = IntParameter(5, 50, default=20, space='sell')
    sell_x2 = IntParameter(50, 1500, default=800, space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Moving Averages
        dataframe['MA_short'] = ta.MA(dataframe, timeperiod=self.x1.value, matype=0)
        dataframe['MA_long'] = ta.MA(dataframe, timeperiod=self.x2.value, matype=0)
        dataframe['MA_short_sell'] = ta.MA(dataframe, timeperiod=self.sell_x1.value, matype=0)
        dataframe['MA_long_sell'] = ta.MA(dataframe, timeperiod=self.sell_x2.value, matype=0)

        # Simplified OTT Indicator calculation
        dataframe['OTT'] = ((dataframe['MA_short'] - dataframe['MA_long']) * 2) + dataframe['MA_long']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Buy conditions
        dataframe.loc[
            (dataframe['MA_short'] > dataframe['OTT']),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Sell conditions based on 'sell' parameters
        dataframe.loc[
            (dataframe['MA_short_sell'] < dataframe['MA_long_sell']),
            'sell'] = 1

        return dataframe
