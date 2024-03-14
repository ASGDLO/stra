from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import DecimalParameter, IntParameter, CategoricalParameter

class CustomADXStrategy(IStrategy):
    """
    ADX ve pivot göstergelerini kullanarak alım ve satım sinyalleri üreten strateji.
    """
    # Strateji parametreleri
    timeframe = '1h'
    stoploss = -0.1  # Stop loss oranı, %10 olarak belirlendi.

    # Hyperopt ile optimize edilecek parametreler
    adx_timeperiod = IntParameter(14, 50, default=14, space='both')  # hem alım hem de satım için kullanılabilir
    adx_trend_threshold_buy = IntParameter(20, 40, default=25, space='buy')  # alım için ADX eşiği
    adx_trend_threshold_sell = IntParameter(20, 40, default=25, space='sell')  # satım için ADX eşiği

    # İndikatörlerin DataFrame'e eklenmesi
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # ADX göstergesi
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_timeperiod.value)

        # YIGIT, ADAM, TX, RX, PVT1, ve PVT2 hesaplamaları
        dataframe['dayofmonth'] = dataframe['date'].dt.day
        dataframe['prev_dayofmonth'] = dataframe['dayofmonth'].shift(1)
        dataframe['YIGIT'] = dataframe['dayofmonth'] > dataframe['prev_dayofmonth']
        dataframe['ADAM'] = dataframe['close'].shift(1).where(dataframe['YIGIT'], float('nan'))
        dataframe['ADAM'].ffill(inplace=True)
        dataframe['TX'] = dataframe['high'].rolling(window=14, min_periods=1).max().shift(1).where(dataframe['YIGIT'], float('nan'))
        dataframe['RX'] = dataframe['low'].rolling(window=14, min_periods=1).min().shift(1).where(dataframe['YIGIT'], float('nan'))
        dataframe['TX'].ffill(inplace=True)
        dataframe['RX'].ffill(inplace=True)
        dataframe['PVT1'] = (dataframe['ADAM'] + dataframe['RX'] + dataframe['TX']) / 3
        dataframe['PVT2'] = dataframe['ADAM']

        return dataframe

    # Alım sinyallerinin oluşturulması
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['adx'] > self.adx_trend_threshold_buy.value) &
                (dataframe['close'] > dataframe['PVT2']) & 
                (dataframe['close'] > dataframe['PVT1'])
            ),
            'buy'] = 1

        return dataframe

    # Satış sinyallerinin oluşturulması
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['adx'] < self.adx_trend_threshold_sell.value) &
                (dataframe['close'] < dataframe['PVT2']) & 
                (dataframe['close'] < dataframe['PVT1'])
            ),
            'sell'] = 1

        return dataframe
