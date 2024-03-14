from pandas import DataFrame
from freqtrade.strategy.interface import IStrategy
import talib.abstract as ta

class PivotBandStrategy(IStrategy):
    """
    Pivot Band Strategy with hourly timeframe and Hyperopt-optimizable parameters
    """
    timeframe = '1h'
    
    stoploss = -0.02
    minimal_roi = {
        "0": 0.01
    }

    custom_info = {
        "ema_period": 3
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        ema_period = self.custom_info.get("ema_period", 3)
        dataframe['EMA'] = ta.EMA(dataframe, timeperiod=ema_period)
        
        dataframe['vPP'] = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        dataframe['vPU'] = 2 * dataframe['vPP'] - dataframe['low']
        dataframe['vPA'] = 2 * dataframe['vPP'] - dataframe['high']
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['EMA'] > dataframe['vPU'])
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['EMA'] < dataframe['vPP'])
            ),
            'exit_long'] = 1
        return dataframe
