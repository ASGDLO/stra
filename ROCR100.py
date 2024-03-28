from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import stoploss_from_open, merge_informative_pair, DecimalParameter, IntParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta

class ROCR100(IStrategy):
    timeframe = '1h'
    stoploss = -0.1
    minimal_roi = {"0": 0.01}

    # Hyperopt parameters
    plus_di_period = IntParameter(5, 30, default=14, space='buy')
    rocr100_period = IntParameter(5, 30, default=10, space='buy')
    stoch_k = IntParameter(5, 30, default=14, space='buy')
    stoch_d = IntParameter(3, 30, default=3, space='buy')
    stddev_period = IntParameter(5, 30, default=5, space='buy')

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['PLUS_DI'] = ta.PLUS_DI(dataframe, timeperiod=self.plus_di_period.value)
        dataframe['PLUS_DM'] = ta.PLUS_DM(dataframe, timeperiod=self.plus_di_period.value)
        dataframe['ROCR100'] = ta.ROCR100(dataframe, timeperiod=self.rocr100_period.value)
        stoch = ta.STOCH(dataframe, fastk_period=self.stoch_k.value, slowk_period=self.stoch_d.value, slowd_period=self.stoch_d.value)
        dataframe['slowk'] = stoch['slowk']
        dataframe['slowd'] = stoch['slowd']
        dataframe['STDDEV'] = ta.STDDEV(dataframe['close'], timeperiod=self.stddev_period.value, nbdev=1.0)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['PLUS_DI'] > 25) &
                (dataframe['ROCR100'] > 100) &
                (dataframe['slowk'] > dataframe['slowd']) &
                (dataframe['STDDEV'] < dataframe['STDDEV'].rolling(window=5).mean())
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['PLUS_DI'] < 20) |
                (dataframe['ROCR100'] < 100) |
                (dataframe['slowk'] < dataframe['slowd']) |
                (dataframe['STDDEV'] > dataframe['STDDEV'].rolling(window=5).mean())
            ),
            'sell'] = 1

        return dataframe
