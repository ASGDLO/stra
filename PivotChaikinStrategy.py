from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class PivotChaikinStrategy(IStrategy):
    INTERFACE_VERSION = 2
    
    # Minimum ROI tanımlanıyor (işlemlerin otomatik olarak kapatılması için gereken minimum kâr oranı)
    minimal_roi = {
        "0": 0.01  # İşlemler en az %1 kar elde ettiğinde kapatılır
    }

    # Stop Loss
    stoploss = -0.1  # Maksimum %10 zarara uğradığında işlem kapatılır

    # Kullanılacak zaman dilimi
    timeframe = '1h'
    
    # Stratejiye özgü parametreler
    sl_s_period = 1
    tp_s_period = 1
    sl_l_period = 1
    tp_l_period = 1
    timeperiod_check = 20  # Pivot hesaplamaları için kullanılan dönem

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Pivot hesaplamaları
        dataframe['pivot'] = (dataframe['low'].rolling(self.timeperiod_check).mean().shift(1) +
                              dataframe['high'].rolling(self.timeperiod_check).mean().shift(1) +
                              dataframe['close'].rolling(self.timeperiod_check).mean().shift(1)) / 3

        # Destek ve direnç seviyeleri
        for i in range(1, 6):
            dataframe[f'Support{i}'] = dataframe['pivot'] - i * (dataframe['high'].rolling(self.timeperiod_check).mean().shift(1) - dataframe['pivot'])
            dataframe[f'Resistance{i}'] = dataframe['pivot'] + i * (dataframe['pivot'] - dataframe['low'].rolling(self.timeperiod_check).mean().shift(1))
        
        # ATR
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # Chaikin A/D Line
        dataframe['ad'] = ta.AD(dataframe)
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Giriş koşulları
        dataframe.loc[
            (
                # Chaikin A/D Line'ın artış göstermesi ve fiyatın pivot üzerinde olması
                (dataframe['ad'] > dataframe['ad'].shift(1)) &
                (dataframe['close'] > dataframe['pivot'])
            ),
            'buy'] = 1
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Çıkış koşulları (Örnek olarak basit bir çıkış stratejisi kullanılmıştır)
        dataframe.loc[
            (
                # Chaikin A/D Line'ın düşüş göstermesi
                (dataframe['ad'] < dataframe['ad'].shift(1))
            ),
            'sell'] = 1

        
        return dataframe
