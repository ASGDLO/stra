from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import numpy as np

class TillsonT3Strategy(IStrategy):
    timeframe = '1h'
    minimal_roi = {"0": 0.01}
    stoploss = -0.1

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        length = 21
        vf = 0.618
        
        ema_first_input = (dataframe['high'] + dataframe['low'] + 2 * dataframe['close']) / 4
        e1 = ta.EMA(ema_first_input, timeperiod=length)
        e2 = ta.EMA(e1, timeperiod=length)
        e3 = ta.EMA(e2, timeperiod=length)
        e4 = ta.EMA(e3, timeperiod=length)
        e5 = ta.EMA(e4, timeperiod=length)
        e6 = ta.EMA(e5, timeperiod=length)

        c1 = -1 * vf * vf * vf
        c2 = 3 * vf * vf + 3 * vf * vf * vf
        c3 = -6 * vf * vf - 3 * vf - 3 * vf * vf * vf
        c4 = 1 + 3 * vf + vf * vf * vf + 3 * vf * vf
        dataframe['TillsonT3'] = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['TillsonT3'] > dataframe['TillsonT3'].shift(1))
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['TillsonT3'] < dataframe['TillsonT3'].shift(1))
            ),
            'sell'] = 1

        return dataframe
