import pandas as pd
import numpy as np
from analysis.market_structure import find_swing_points

def detect_liquidity_sweep(df: pd.DataFrame, lookback: int = 10) -> dict:
    df = find_swing_points(df)
    
    recent = df.tail(lookback + 5)
    
    swing_highs = recent['Swing_High'].dropna()
    swing_lows = recent['Swing_Low'].dropna()

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return {
            "buy_side_liquidity": None,
            "sell_side_liquidity": None,
            "swept_buy_side": False,
            "swept_sell_side": False,
            "sweep_direction": None
        }

    last_swing_high = swing_highs.iloc[-1]
    last_swing_low = swing_lows.iloc[-1]

    current_high = df['High'].iloc[-1]
    current_low = df['Low'].iloc[-1]
    current_close = df['Close'].iloc[-1]

    swept_buy_side = False
    if current_high > last_swing_high and current_close < last_swing_high:
        swept_buy_side = True

    swept_sell_side = False
    if current_low < last_swing_low and current_close > last_swing_low:
        swept_sell_side = True

    sweep_direction = None
    if swept_sell_side and not swept_buy_side:
        sweep_direction = "bullish"
    elif swept_buy_side and not swept_sell_side:
        sweep_direction = "bearish"

    return {
        "buy_side_liquidity": float(last_swing_high),
        "sell_side_liquidity": float(last_swing_low),
        "swept_buy_side": swept_buy_side,
        "swept_sell_side": swept_sell_side,
        "sweep_direction": sweep_direction
    }


def get_liquidity_analysis(df: pd.DataFrame) -> dict:
    sweep_info = detect_liquidity_sweep(df)
    
    return {
        "buy_side_liquidity": sweep_info["buy_side_liquidity"],
        "sell_side_liquidity": sweep_info["sell_side_liquidity"],
        "liquidity_sweep": sweep_info["sweep_direction"],
        "swept_buy_side": sweep_info["swept_buy_side"],
        "swept_sell_side": sweep_info["swept_sell_side"]
  }
