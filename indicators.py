import pandas as pd
import numpy as np

def calculate_rsi(df, period=14):
    """Calculate RSI (14 periods)."""
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else None

def calculate_ma(df, window):
    """Calculate moving average."""
    return df['Close'].rolling(window=window).mean().iloc[-1] if len(df) >= window else None

def calculate_macd(df):
    """Calculate MACD (12,26,9)."""
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

def volume_trend(df):
    """Determine volume trend."""
    if len(df) < 50:
        return 'N/A'
    avg_vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
    avg_vol_50 = df['Volume'].rolling(50).mean().iloc[-1]
    if avg_vol_20 > avg_vol_50 * 1.1:
        return 'Increasing'
    elif avg_vol_20 < avg_vol_50 * 0.9:
        return 'Decreasing'
    return 'Stable'

def trend_direction(df):
    """Determine trend direction with confirmation."""
    ma20 = calculate_ma(df, 20)
    ma50 = calculate_ma(df, 50)
    ma200 = calculate_ma(df, 200)
    close = df['Close'].iloc[-1]
    if ma20 is None or ma50 is None or ma200 is None:
        return 'N/A'
    if close > ma20 and ma20 > ma50 and ma50 > ma200:
        return 'Up'
    elif close < ma20 and ma20 < ma50 and ma50 < ma200:
        return 'Down'
    return 'Sideways'

def get_technical_indicators(history):
    """Aggregate all technical indicators."""
    indicators = {}
    indicators['rsi'] = calculate_rsi(history)
    indicators['ma20'] = calculate_ma(history, 20)
    indicators['ma50'] = calculate_ma(history, 50)
    indicators['ma200'] = calculate_ma(history, 200)
    indicators['macd'], indicators['signal'] = calculate_macd(history)
    indicators['volume_trend'] = volume_trend(history)
    indicators['trend'] = trend_direction(history)
    return indicators
