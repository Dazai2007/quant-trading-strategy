import numpy as np
import pandas as pd
from scipy.stats import norm

class Indicators:
    @staticmethod
    def ma_crossover(df, short_window=50, long_window=200):
        df['ma_short'] = df['close'].rolling(window=short_window).mean()
        df['ma_long'] = df['close'].rolling(window=long_window).mean()
        return df

    @staticmethod
    def rsi(df, window=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def bollinger_bands(df, window=20, num_std=2):
        df['bb_mid'] = df['close'].rolling(window=window).mean()
        df['bb_std'] = df['close'].rolling(window=window).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * num_std)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * num_std)
        return df

    @staticmethod
    def atr(df, window=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(window=window).mean()
        return df

    @staticmethod
    def adx(df, window=14):
        """
        Calculate Average Directional Index (ADX).
        """
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = pd.DataFrame(df['high'] - df['low'])
        tr2 = pd.DataFrame(abs(df['high'] - df['close'].shift(1)))
        tr3 = pd.DataFrame(abs(df['low'] - df['close'].shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
        
        atr = tr.rolling(window).mean()
        
        plus_di = 100 * (plus_dm.ewm(alpha=1/window).mean() / atr)
        minus_di = 100 * (abs(minus_dm).ewm(alpha=1/window).mean() / atr)
        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (window - 1)) + dx) / window
        adx_smooth = adx.ewm(alpha=1/window).mean()
        
        df['adx'] = adx_smooth
        return df

    @staticmethod
    def garch_volatility(df):
        from arch import arch_model
        returns = 100 * df['close'].pct_change().dropna()
        am = arch_model(returns, vol='Garch', p=1, o=0, q=1, dist='Normal')
        res = am.fit(disp='off')
        df['garch_vol'] = res.conditional_volatility
        return df
