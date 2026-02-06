import numpy as np
from config import SCORING_THRESHOLDS

def fundamental_score(data):
    """Calculate fundamental score (0-100)."""
    scores = []
    # Valuation
    if 'pe' in data and data['pe'] is not None:
        scores.append(max(0, min(100, 150 - data['pe'] * 5)))  # PE<15=100, >30=0
    if 'pbv' in data and data['pbv'] is not None:
        scores.append(max(0, min(100, 150 - data['pbv'] * 50)))  # PBV<2=100, >3=0
    # Profitability
    if 'eps' in data and data['eps'] is not None:
        scores.append(min(100, max(0, data['eps'] * 10)) if data['eps'] > 0 else 0)
    if 'roe' in data and data['roe'] is not None:
        scores.append(min(100, max(0, (data['roe'] - 0.05) * 500)))  # ROE>0.25=100
    # Debt
    if 'debt_equity' in data and data['debt_equity'] is not None:
        scores.append(max(0, min(100, 150 - data['debt_equity'] * 50)))  # <1=100, >3=0
    # Growth & Margin
    if 'revenue_growth' in data and data['revenue_growth'] is not None:
        scores.append(min(100, max(0, data['revenue_growth'] * 2)))
    if 'net_margin' in data and data['net_margin'] is not None:
        scores.append(min(100, max(0, data['net_margin'] * 4)))
    return np.mean(scores) if scores else 0

def technical_score(indicators):
    """Calculate technical score (0-100) with confirmation logic."""
    scores = []
    # RSI zone with trend confirmation
    rsi = indicators['rsi'] if indicators['rsi'] is not None else 50
    trend = indicators['trend']
    rsi_score = 50
    if rsi < 30 and trend != 'Down': rsi_score = 100  # Buy signal if not downtrend
    elif rsi > 70 and trend != 'Up': rsi_score = 0  # Sell signal if not uptrend
    scores.append(rsi_score)
    # MA alignment
    ma_score = 100 if trend == 'Up' else 50 if trend == 'Sideways' else 0
    scores.append(ma_score)
    # MACD momentum
    macd, signal = indicators['macd'], indicators['signal']
    macd_score = 100 if macd > signal and macd > 0 else 0 if macd < signal and macd < 0 else 50
    scores.append(macd_score)
    # Volume confirmation
    vol_score = 100 if indicators['volume_trend'] == 'Increasing' else 50 if indicators['volume_trend'] == 'Stable' else 0
    scores.append(vol_score)
    return np.mean(scores) if scores else 0

def risk_score(data, history):
    """Calculate risk score (0-100)."""
    scores = []
    # Volatility
    if not history.empty:
        returns = history['Close'].pct_change().dropna()
        vol = returns.std() * np.sqrt(252)
        scores.append(max(0, 100 - vol * 200))  # <0.3=100, >0.5=0
    # Liquidity
    if 'volume' in data and data['volume']:
        scores.append(min(100, data['volume'] / 1e6 * 10))  # Arbitrary scale
    # Market cap stability
    if 'market_cap' in data and data['market_cap']:
        scores.append(min(100, data['market_cap'] / 1e9 * 10))
    # Gorengan detection (small cap high vol)
    penalty = -50 if 'market_cap' in data and data['market_cap'] < 1e9 and vol > 0.5 else 0
    return max(0, min(100, np.mean(scores) + penalty if scores else 0))

def calculate_scores(data, history, indicators):
    """Aggregate scores with weights and penalties."""
    missing_count = sum(1 for v in data.values() if v is None)
    missing_penalty = missing_count * 10  # Penalty per missing field
    f = fundamental_score(data) - missing_penalty / 2
    t = technical_score(indicators)
    r = risk_score(data, history) - missing_penalty / 2
    final = 0.4 * max(0, f) + 0.35 * t + 0.25 * max(0, r)
    return max(0, min(100, f)), t, max(0, min(100, r)), min(100, final), missing_penalty
