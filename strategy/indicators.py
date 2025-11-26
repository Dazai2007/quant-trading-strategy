import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def donchian_channel(df, window=20):
        """
        Calculate Donchian Channels.
        """
        df['donchian_high'] = df['high'].rolling(window=window).max()
        df['donchian_low'] = df['low'].rolling(window=window).min()
        df['donchian_mid'] = (df['donchian_high'] + df['donchian_low']) / 2
        return df

    @staticmethod
    def ma_crossover(df, short_window=50, long_window=200):
        """
        Calculate Moving Average Crossover.
        """
        df['ma_short'] = df['close'].rolling(window=short_window).mean()
        df['ma_long'] = df['close'].rolling(window=long_window).mean()
        return df

    @staticmethod
    def rsi(df, window=14):
        """
        Calculate Relative Strength Index (RSI).
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def bollinger_bands(df, window=20, num_std=2):
        """
        Calculate Bollinger Bands.
        """
        df['bb_mid'] = df['close'].rolling(window=window).mean()
        df['bb_std'] = df['close'].rolling(window=window).std()
        df['bb_upper'] = df['bb_mid'] + (df['bb_std'] * num_std)
        df['bb_lower'] = df['bb_mid'] - (df['bb_std'] * num_std)
        return df

    @staticmethod
    def atr(df, window=14):
        """
        Calculate Average True Range (ATR).
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(window=window).mean()
        return df

    @staticmethod
    def garch_volatility(df):
        """
        Estimate Volatility using GARCH(1,1).
        Requires 'arch' library.
        """
        from arch import arch_model
        returns = df['close'].pct_change().dropna() * 100 # Rescale for numerical stability
        model = arch_model(returns, vol='Garch', p=1, q=1)
        res = model.fit(disp='off')
        df['garch_vol'] = np.nan
        # Forecast volatility (conditional volatility)
        # Note: This is a simplified application. In a real loop, you'd refit or update.
        df.loc[returns.index, 'garch_vol'] = res.conditional_volatility
        return df
