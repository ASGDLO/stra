from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import numpy as np
from scipy import stats

class TrendChannelStrategy(IStrategy):
    timeframe = '1d'
    minimal_roi = {"0": 0.01}
    stoploss = -0.1
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Trend çizgisinin hesaplanması için gerekli olan minimum veri sayısını belirleyin
        min_periods = 30

        # x_range, DataFrame'in index boyutuna eşit olacak şekilde ayarlanır
        x_range = np.arange(len(dataframe))
        
        # Eğim ve kesme noktasını hesaplamak için kullanılacak kapanış fiyatlarını seçin
        # Bu örnekte, tüm veri seti üzerinde eğim ve kesme noktası hesaplanıyor
        # Ancak, sadece son 'min_periods' kullanılarak bir trend çizgisi çizmek isteyebilirsiniz
        slope, intercept, r_value, _, _ = stats.linregress(x_range[-min_periods:], dataframe['close'].tail(min_periods))
        
        # Tüm DataFrame için trend çizgisini hesaplayın
        dataframe['trend_line'] = slope * x_range + intercept

        # R değeri ve diğer istatistikleri DataFrame'e ekleyin
        dataframe['trend_slope'] = slope
        dataframe['trend_intercept'] = intercept
        dataframe['r_value'] = r_value

        return dataframe



    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # R değeri yüksek ve fiyat trend çizgisinin üzerindeyse alım yapın
                (dataframe['r_value'].abs() > 0.8) &
                (dataframe['close'] > dataframe['trend_line'])
            ),
            'buy'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # R değeri düşük veya fiyat trend çizgisinin altına düşerse satış yapın
                (dataframe['r_value'].abs() < 0.8) |
                (dataframe['close'] < dataframe['trend_line'])
            ),
            'sell'] = 1

        return dataframe
