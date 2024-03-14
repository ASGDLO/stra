from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import numpy as np
import pandas as pd
from freqtrade.strategy import DecimalParameter, IntParameter

class MultipleOTTStrategy(IStrategy):
    """
    Multiple OTT Strategy for Freqtrade with Hyperopt Optimization for both Buy and Sell signals.
    """
    
    # Alım için Hyperopt parametre aralıklarını tanımla
    buy_ott_length = IntParameter(1, 21, default=1, space='buy')
    buy_ott_percent = DecimalParameter(0.1, 4.0, default=2.2, space='buy')

    # Satım için Hyperopt parametre aralıklarını tanımla
    sell_ott_length = IntParameter(1, 21, default=1, space='sell')
    sell_ott_percent = DecimalParameter(0.1, 4.0, default=2.2, space='sell')

    # Strateji parametreleri
    minimal_roi = {
        "0": 0.01  # Minimum %1 Return on Investment
    }
    stoploss = -0.10  # %10 stop-loss
    timeframe = '1h'  # Zaman aralığı
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Göstergeleri hesaplayan fonksiyon.
        """
        # Alım göstergeleri
        dataframe['buy_ott'], dataframe['buy_long_stop'], dataframe['buy_short_stop'] = self.ott(
            dataframe['close'], self.buy_ott_length.value, self.buy_ott_percent.value)
        
        # Satım göstergeleri
        dataframe['sell_ott'], dataframe['sell_long_stop'], dataframe['sell_short_stop'] = self.ott(
            dataframe['close'], self.sell_ott_length.value, self.sell_ott_percent.value)
        
        return dataframe

    def ott(self, close, length, percent):
        """
        OTT Göstergesi hesaplama fonksiyonu.
        """
        fark = close * percent / 100
        long_stop = close - fark
        short_stop = close + fark

        long_stop = long_stop.shift(1).where(long_stop > long_stop.shift(1), long_stop)
        short_stop = short_stop.shift(1).where(short_stop < short_stop.shift(1), short_stop)

        ott = np.where(close > long_stop, long_stop, np.where(close < short_stop, short_stop, np.nan))
        ott = pd.Series(ott, index=close.index).ffill().bfill()

        return ott, long_stop, short_stop

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Alım (giriş) koşullarını belirleyen fonksiyon.
        """
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['buy_ott'])  # Fiyat Alım OTT'nin üzerindeyse al
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Satım (çıkış) koşullarını belirleyen fonksiyon.
        """
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['sell_ott'])  # Fiyat Satım OTT'nin altındaysa sat
            ),
            'sell'] = 1

        return dataframe
