from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class RectangleBottomStrategy(IStrategy):
    """
    Bu strateji, dikdörtgenin altından bir kırılma gerçekleştiğinde alım yapar
    ve belirlenen yüzde kazancı elde ettiğinde veya üç işlem günü sonra satış yapar.
    """
    # Stratejinin parametreleri
    timeframe = '1h'
    minimal_roi = {
        "0": 0.05,  # %5 kazanç elde edildiğinde sat
        "3": 0.0  # 3 gün sonra her durumda sat
    }
    stoploss = -0.10  # %10 stop loss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    def informative_pairs(self):
        # İlave veri çiftleri
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Fiyat hareketini analiz etmek için indikatörler
        # Örnek: 200 gün ve 50 gün basit hareketli ortalamalar
        dataframe['sma200'] = ta.SMA(dataframe, timeperiod=200)
        dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)
        
        # Burada ilave indikatörler eklenebilir

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Alım sinyalleri burada tanımlanır.
        Örneğin: Fiyat SMA 200'ün üzerinde ve SMA 50'nin altından SMA 50'nin üzerine çıktığında al
        """
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['sma200']) &  # Fiyat 200 günlük SMA'nın üzerinde
                (dataframe['close'].shift(1) < dataframe['sma50']) &  # Dün SMA 50'nin altındaydı
                (dataframe['close'] > dataframe['sma50'])  # Bugün SMA 50'nin üzerine çıktı
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Satış sinyalleri burada tanımlanır.
        Bu strateji, minimal_roi ayarlarına göre otomatik satış yapacak,
        bu yüzden burası boş bırakılabilir veya özel bir satış stratejisi tanımlanabilir.
        """
        # Özel bir satış stratejisi için:
        # dataframe.loc[
        #     (
        #         # Özel bir satış koşulu
        #     ),
        #     'sell'] = 1

        return dataframe
