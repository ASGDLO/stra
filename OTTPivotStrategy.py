from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import stoploss_from_open, merge_informative_pair, DecimalParameter, IntParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np
import pandas as pd

class OTTPivotStrategy(IStrategy):
    timeframe = '1m'
    stoploss = -0.1
    minimal_roi = {"0": 0.01}

    # Hyperopt parameters for buy signals
    ott_length = IntParameter(10, 30, default=21, space='buy')
    ott_percent = DecimalParameter(0.5, 0.9, default=0.7, space='buy')
    pivot_lookback = IntParameter(3, 14, default=7, space='buy')


    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Pivot Points, Supports and Resistances
        PP = pd.Series((dataframe['high'] + dataframe['low'] + dataframe['close']) / 3)
        R1 = pd.Series(2 * PP - dataframe['low'])
        S1 = pd.Series(2 * PP - dataframe['high'])
        R2 = pd.Series(PP + dataframe['high'] - dataframe['low'])
        S2 = pd.Series(PP - dataframe['high'] + dataframe['low'])
        R3 = pd.Series(dataframe['high'] + 2 * (PP - dataframe['low']))
        S3 = pd.Series(dataframe['low'] - 2 * (dataframe['high'] - PP))
        
        dataframe['PP'] = PP
        dataframe['R1'] = R1
        dataframe['S1'] = S1
        dataframe['R2'] = R2
        dataframe['S2'] = S2
        dataframe['R3'] = R3
        dataframe['S3'] = S3

        # OTT Indicator
        length = self.ott_length.value
        percent = self.ott_percent.value
        alpha = 2 / (length + 1)
        
        dataframe['ud1'] = np.where(dataframe['close'] > dataframe['close'].shift(1), dataframe['close'] - dataframe['close'].shift(), 0)
        dataframe['dd1'] = np.where(dataframe['close'] < dataframe['close'].shift(1), dataframe['close'].shift() - dataframe['close'], 0)
        dataframe['UD'] = dataframe['ud1'].rolling(window=9).sum()
        dataframe['DD'] = dataframe['dd1'].rolling(window=9).sum()
        dataframe['CMO'] = ((dataframe['UD'] - dataframe['DD']) / (dataframe['UD'] + dataframe['DD'])).fillna(0).abs()

        dataframe['Var'] = ta.EMA(dataframe['CMO'] * dataframe['close'], int(length))
        dataframe['fark'] = dataframe['Var'] * percent * 0.01
        dataframe['OTT'] = np.where(dataframe['close'] > dataframe['Var'], dataframe['Var'] + dataframe['fark'], dataframe['Var'] - dataframe['fark'])

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['OTT']) &
                (dataframe['close'] > dataframe['PP'])
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['OTT']) |
                (dataframe['close'] < dataframe['S1'])
            ),
            'sell'] = 1

        return dataframe
