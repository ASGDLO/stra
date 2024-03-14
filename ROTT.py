from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class ROTT(IStrategy):
    """
    Hareketli Ortalamalar ve OTT Göstergesi kullanarak alım ve satım sinyalleri üreten strateji.
    """
    # Strateji parametreleri
    timeframe = '1m'
    stoploss = -0.1  # Stop loss oranı, %10 olarak belirlendi.
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Hareketli Ortalamalar
        x1 = 30
        x2 = 1000
        dataframe['MA_short'] = ta.MA(dataframe, timeperiod=x1, matype=0)
        dataframe['MA_long'] = ta.MA(dataframe, timeperiod=x2, matype=0)
        
        # OTT Göstergesi hesaplama (burada basitleştirilmiş bir versiyon kullanılacaktır)
        dataframe['OTT'] = ((dataframe['MA_short'] - dataframe['MA_long']) * 2) + dataframe['MA_long']
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Alım koşulları
        dataframe.loc[
            (
                dataframe['MA_short'] > dataframe['OTT']
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Satım koşulları
        dataframe.loc[
            (
                dataframe['MA_short'] < dataframe['OTT']
            ),
            'sell'] = 1

        return dataframe
